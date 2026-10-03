"""Gera o site estático do Dicas de Django a partir de SUMMARY.md e docs/*.md.

Uso:
    python site/build.py            # gera em _site/
    python site/build.py --base /dicas-de-django/

Dependências: markdown, pygments.
"""
import datetime
import html
import json
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import quote

import markdown
from pygments.formatters import HtmlFormatter

ROOT = Path(__file__).resolve().parent.parent
THEME = ROOT / 'site' / 'theme'
OUT = ROOT / '_site'
REPO_URL = 'https://github.com/rg3915/dicas-de-django'
YOUTUBE_URL = 'https://www.youtube.com/@RegisdoPython'
SITE_URL = 'https://www.dicas-de-django.com.br'
AUTOR = {'@type': 'Person', 'name': 'Regis Santos', 'alternateName': 'Regis do Python',
         'url': YOUTUBE_URL, 'sameAs': [YOUTUBE_URL, 'https://github.com/rg3915', 'https://x.com/rg3915']}

# Seções da barra lateral, pelo número do arquivo em docs/.
SECOES = [
    (0, 60, 'Primeira série (2020 e 2021)'),
    (61, 102, 'Projeto Dicas de Django (2022 e 2023)'),
    (103, 110, 'Django 5 e ferramentas'),
    (111, 125, 'Django 6 e projetos'),
    (126, 9999, 'Novas dicas'),
]


def secao(numero_arquivo):
    for ini, fim, nome in SECOES:
        if ini <= numero_arquivo <= fim:
            return nome
    return SECOES[-1][2]


def ler_sumario():
    itens = []
    for linha in (ROOT / 'SUMMARY.md').read_text(encoding='utf-8').splitlines():
        m = re.match(r'\*\s*\[(.+?)\]\((docs/[^)]+\.md)\)', linha.strip())
        if not m:
            continue
        titulo, caminho = m.groups()
        slug = Path(caminho).stem
        num = re.match(r'Dica\s+([\d.]+)\s*[-–]\s*(.+)', titulo)
        if num:
            numero, nome = num.group(1).lstrip('0') or '0', num.group(2)
        else:
            numero, nome = '', titulo
        itens.append({
            'slug': slug,
            'arquivo': ROOT / caminho,
            'numero': numero,
            'nome': nome,
            'secao': secao(int(slug[:3])),
        })
    return itens


def preparar_markdown(texto):
    # front matter do GitBook
    texto = re.sub(r'\A---\n.*?\n---\n', '', texto, flags=re.S)
    # O GitBook exigia escapar as tags do Django; aqui elas aparecem como devem.
    texto = texto.replace('{\\%', '{%').replace('%\\}', '%}').replace('{\\{', '{{').replace('}\\}', '}}')
    # aviso do GitBook sobre as tags escapadas: aqui as tags já aparecem certas
    texto = re.sub(r'\*\*Importante:\*\* remova a `\\` no meio das tags\.\s*\n', '', texto)
    texto = re.sub(r'!\[\]\((?:\.\./)?\.gitbook/assets/tags\.png\)\s*\n', '', texto)
    # imagens e assets
    texto = texto.replace('../.gitbook/assets/', '../assets/').replace('./.gitbook/assets/', 'assets/')
    # links entre páginas (arquivo.md -> ../slug/)
    texto = re.sub(r'\]\((?:\.\./)?(?:docs/)?(\d{3}-[\w-]+)\.md(#[^)]*)?\)', lambda m: f'](../{m.group(1)}/{m.group(2) or ""})', texto)
    return texto


def renderizar(texto):
    md = markdown.Markdown(
        extensions=['fenced_code', 'codehilite', 'tables', 'toc', 'attr_list', 'sane_lists'],
        extension_configs={
            'codehilite': {'css_class': 'hl', 'guess_lang': False},
            'toc': {'permalink': False},
        },
        output_format='html5',
    )
    corpo = md.convert(texto)
    toc = [t for t in md.toc_tokens]
    return corpo, toc


def texto_alt(src):
    nome = Path(src).stem
    if nome == 'youtube':
        return 'Assistir ao vídeo no YouTube'
    nome = re.sub(r'^[\d_\-.]+', '', nome)
    nome = re.sub(r'[_\-]+', ' ', nome).strip()
    if nome.endswith(' er'):
        return 'Diagrama entidade-relacionamento: ' + nome[:-3]
    return 'Imagem: ' + nome if nome else 'Imagem ilustrativa'


def ajustar_imagens(corpo):
    def troca(m):
        tag = m.group(0)
        src = re.search(r'src="([^"]*)"', tag)
        if not src:
            return tag
        if not re.search(r'alt="[^"]+"', tag):
            tag = re.sub(r'\salt="[^"]*"', '', tag)
            tag = tag.replace('<img', f'<img alt="{html.escape(texto_alt(src.group(1)))}"', 1)
        if 'loading=' not in tag:
            tag = tag.replace('<img', '<img loading="lazy" decoding="async"', 1)
        return tag
    return re.sub(r'<img\b[^>]*>', troca, corpo)


def ajustar_titulos(corpo):
    # o h1 é o título da página; no corpo os níveis começam em h2 e não pulam
    ultimo, abertos = 1, []

    def troca(m):
        nonlocal ultimo
        barra, nivel, resto = m.group(1), int(m.group(2)), m.group(3)
        if barra:
            return f'</h{abertos.pop()}>'
        novo = min(max(nivel, 2), ultimo + 1)
        ultimo = novo
        abertos.append(novo)
        return f'<h{novo}{resto}>'
    return re.sub(r'<(/?)h([1-6])(\b[^>]*)>', troca, corpo)


def codigo_focavel(corpo):
    # blocos com rolagem horizontal precisam receber foco pelo teclado
    return re.sub(r'<pre(?![^>]*tabindex)', '<pre tabindex="0"', corpo)


def youtube_id(texto):
    m = re.search(r'youtu(?:\.be/|be\.com/(?:watch\?v=|shorts/|embed/))([\w-]{11})', texto)
    return m.group(1) if m else None


def data_publicacao(texto):
    m = re.search(r'Publicado em (\d{2})/(\d{2})/(\d{4})', texto)
    if not m:
        return None
    d = datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    return d if d <= datetime.date.today() else None


def descricao(corpo, titulo):
    for p in re.findall(r'<p>(.*?)</p>', corpo, flags=re.S):
        t = ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', p)).split())
        if re.fullmatch(r'\s*<a\b.*</a>\s*', p, flags=re.S):
            continue
        if (len(t.split()) < 9 or 'http' in t or t.endswith(':')
                or t.startswith(('Publicado em', 'Documentação', 'Github', 'GitHub', 'Doc', 'Importante'))):
            continue
        if len(t) > 155:
            t = t[:155].rsplit(' ', 1)[0].rstrip(',.;:') + '…'
        return t
    nome = re.sub(r'^Dica\s+[\d.]+\s*[-–]\s*', '', titulo)
    return f'{nome}: tutorial de Django em português, com código e explicação passo a passo, por Regis do Python.'


def json_ld(dados):
    return '<script type="application/ld+json">' + json.dumps(dados, ensure_ascii=False).replace('</', '<\\/') + '</script>'


def tirar_h1(corpo):
    m = re.search(r'<h1[^>]*>(.*?)</h1>', corpo, flags=re.S)
    if not m:
        return corpo, None
    return corpo[:m.start()] + corpo[m.end():], re.sub('<[^>]+>', '', m.group(1)).strip()


def texto_puro(corpo):
    sem_codigo = re.sub(r'<pre.*?</pre>', ' ', corpo, flags=re.S)
    return html.unescape(re.sub(r'<[^>]+>', ' ', sem_codigo))


def minutos(corpo):
    palavras = len(re.findall(r'\w+', re.sub(r'<[^>]+>', ' ', corpo)))
    return max(1, round(palavras / 200))


def lateral(itens, atual):
    blocos, ultima = [], None
    for it in itens:
        if it['secao'] != ultima:
            if ultima is not None:
                blocos.append('</ol></details>')
            aberta = ' open' if any(i['slug'] == atual and i['secao'] == it['secao'] for i in itens) or (atual is None and it['secao'] == SECOES[3][2]) else ''
            blocos.append(f'<details{aberta}><summary>{html.escape(it["secao"])}</summary><ol>')
            ultima = it['secao']
        cur = ' aria-current="page"' if it['slug'] == atual else ''
        blocos.append(f'<li><a href="../{it["slug"]}/"{cur}><span>{html.escape(it["numero"])}</span>{html.escape(it["nome"])}</a></li>')
    blocos.append('</ol></details>')
    return '\n'.join(blocos)


def nesta_pagina(corpo):
    links = []
    for ident, nome in re.findall(r'<h2 id="([^"]+)"[^>]*>(.*?)</h2>', corpo, flags=re.S):
        nome = html.unescape(re.sub(r'<[^>]+>', '', nome)).strip()
        links.append(f'<a href="#{ident}">{html.escape(nome)}</a>')
    if not links:
        return ''
    return '<nav class="toc" aria-label="Nesta página"><p>Nesta página</p>' + ''.join(links) + '</nav>'


def _luminancia(hexa):
    r, g, b = (int(hexa[i:i + 2], 16) / 255 for i in (0, 2, 4))
    lin = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def _contraste(a, b):
    la, lb = sorted((_luminancia(a), _luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def com_contraste(css, fundo, minimo=4.6):
    # escurece (ou clareia, no tema escuro) as cores do Pygments até passar no WCAG AA
    escuro = _luminancia(fundo) < 0.2

    def ajusta(m):
        cor = m.group(1)
        if len(cor) == 3:
            cor = ''.join(c * 2 for c in cor)
        rgb = [int(cor[i:i + 2], 16) for i in (0, 2, 4)]
        for _ in range(40):
            atual = ''.join(f'{c:02x}' for c in rgb)
            if _contraste(atual, fundo) >= minimo:
                break
            rgb = [min(255, c + 8) if escuro else max(0, c - 8) for c in rgb]
        return 'color: #' + ''.join(f'{c:02x}' for c in rgb)
    return re.sub(r'(?<![-\w])color: #([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b', ajusta, css)


def preencher(modelo, valores):
    # uma passada só: o conteúdo inserido nunca é reprocessado
    return re.sub(r'\{\{\w+\}\}', lambda m: valores.get(m.group(0), m.group(0)), modelo)


def main():
    base = '/'
    if '--base' in sys.argv:
        base = sys.argv[sys.argv.index('--base') + 1]
    modelo = (THEME / 'page.html').read_text(encoding='utf-8')
    itens = ler_sumario()

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / 'assets').mkdir(parents=True)
    shutil.copytree(ROOT / '.gitbook' / 'assets', OUT / 'assets', dirs_exist_ok=True)
    if (ROOT / 'img').exists():
        shutil.copytree(ROOT / 'img', OUT / 'img')
    for f in THEME.iterdir():
        if f.suffix in ('.css', '.js', '.svg', '.png', '.ico'):
            shutil.copy(f, OUT / 'assets' / f.name)
    # cores do código (Pygments) para os dois temas
    claro = com_contraste(HtmlFormatter(style='friendly').get_style_defs('.hl'), 'EDF2EE')
    escuro = com_contraste(HtmlFormatter(style='github-dark').get_style_defs('.hl'), '14221C')
    regras = [linha for linha in escuro.splitlines() if linha.startswith('.hl')]
    escolhido = '\n'.join(f':root[data-theme="dark"] {linha}' for linha in regras)
    sistema = '\n'.join(f':root:not([data-theme="light"]) {linha}' for linha in regras)
    escuro = escolhido + '\n@media (prefers-color-scheme: dark) {\n' + sistema + '\n}'
    (OUT / 'assets' / 'code.css').write_text(claro + '\n' + escuro, encoding='utf-8')

    busca = []
    mapa = []
    for n, it in enumerate(itens):
        bruto = preparar_markdown(it['arquivo'].read_text(encoding='utf-8'))
        corpo, toc = renderizar(bruto)
        corpo, h1 = tirar_h1(corpo)
        corpo = codigo_focavel(ajustar_imagens(ajustar_titulos(corpo)))
        titulo = h1 or it['nome']
        url = f'{SITE_URL}/{it["slug"]}/'
        desc = descricao(corpo, titulo)
        video = youtube_id(bruto)
        pendente = 'yt-pending' in bruto or 'yt-block' in bruto or 'agendado' in bruto
        data = data_publicacao(bruto)
        imagem = f'https://i.ytimg.com/vi/{video}/hqdefault.jpg' if video and not pendente else f'{SITE_URL}/assets/og.png'
        artigo = {
            '@context': 'https://schema.org', '@type': 'TechArticle', 'headline': titulo[:110],
            'description': desc, 'url': url, 'mainEntityOfPage': url, 'inLanguage': 'pt-BR',
            'image': imagem, 'author': AUTOR, 'publisher': AUTOR,
            'isPartOf': {'@type': 'WebSite', 'name': 'Dicas de Django', 'url': SITE_URL + '/'},
        }
        if data:
            artigo['datePublished'] = data.isoformat()
        if video and not pendente:
            artigo['video'] = {'@type': 'VideoObject', 'name': titulo, 'description': desc,
                               'thumbnailUrl': imagem, 'embedUrl': f'https://www.youtube.com/embed/{video}',
                               'contentUrl': f'https://www.youtube.com/watch?v={video}'}
            if data:
                artigo['video']['uploadDate'] = data.isoformat()
        trilha = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Dicas de Django', 'item': SITE_URL + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': it['secao'], 'item': SITE_URL + '/'},
            {'@type': 'ListItem', 'position': 3, 'name': titulo, 'item': url}]}
        mapa.append((url, data))
        ant = itens[n - 1] if n > 0 else None
        prox = itens[n + 1] if n + 1 < len(itens) else None
        navega = '<nav class="vizinhos" aria-label="Dica anterior e próxima">'
        navega += f'<a href="../{ant["slug"]}/" rel="prev"><small>Anterior</small>{html.escape(ant["nome"])}</a>' if ant else '<span></span>'
        navega += f'<a href="../{prox["slug"]}/" rel="next"><small>Próxima</small>{html.escape(prox["nome"])}</a>' if prox else '<span></span>'
        navega += '</nav>'
        valores = {
            '{{titulo_pagina}}': html.escape(f'{titulo} | Dicas de Django'),
            '{{descricao}}': html.escape(desc),
            '{{url}}': url,
            '{{imagem}}': imagem,
            '{{data}}': f'<meta property="article:published_time" content="{data.isoformat()}">' if data else '',
            '{{jsonld}}': json_ld(artigo) + json_ld(trilha),
            '{{lateral}}': lateral(itens, it['slug']),
            '{{numero}}': html.escape(it['numero']),
            '{{numero_classe}}': '' if it['numero'] else ' sem-numero',
            '{{titulo}}': html.escape(titulo),
            '{{secao}}': html.escape(it['secao']),
            '{{minutos}}': str(minutos(corpo)),
            '{{corpo}}': corpo,
            '{{toc}}': nesta_pagina(corpo),
            '{{vizinhos}}': navega,
            '{{editar}}': f'{REPO_URL}/blob/master/docs/{it["arquivo"].name}',
            '{{raiz}}': '../',
            '{{youtube}}': YOUTUBE_URL,
            '{{repo}}': REPO_URL,
            '{{base}}': base,
        }
        pagina = preencher(modelo, valores)
        destino = OUT / it['slug']
        destino.mkdir()
        (destino / 'index.html').write_text(pagina, encoding='utf-8')
        busca.append({'s': it['slug'], 'n': it['numero'], 't': titulo, 'c': it['secao'], 'x': ' '.join(texto_puro(corpo).split())[:3000]})

    (OUT / 'assets' / 'busca.json').write_text(json.dumps(busca, ensure_ascii=False), encoding='utf-8')

    # página inicial
    home = (THEME / 'home.html').read_text(encoding='utf-8')
    recentes = list(reversed(itens))[:12]
    cards = ''.join(
        f'<li><a href="{it["slug"]}/"><span>{html.escape(it["numero"])}</span><b>{html.escape(it["nome"])}</b></a></li>'
        for it in recentes
    )
    site = {'@context': 'https://schema.org', '@type': 'WebSite', 'name': 'Dicas de Django',
            'url': SITE_URL + '/', 'inLanguage': 'pt-BR', 'author': AUTOR,
            'description': 'Tutoriais de Django em português, com o código completo de cada vídeo do canal Regis do Python.'}
    home = preencher(home, {
        '{{jsonld}}': json_ld(site),
        '{{url}}': SITE_URL + '/',
        '{{imagem}}': f'{SITE_URL}/assets/og.png',
        '{{lateral}}': lateral(itens, None).replace('href="../', 'href="'),
        '{{recentes}}': cards,
        '{{total}}': str(len([i for i in itens if i['numero']])),
        '{{raiz}}': '',
        '{{youtube}}': YOUTUBE_URL,
        '{{repo}}': REPO_URL,
        '{{base}}': base,
    })
    (OUT / 'index.html').write_text(home, encoding='utf-8')
    erro = home.replace('<meta name="robots" content="index, follow">', '<meta name="robots" content="noindex">')
    erro = re.sub(r'<link rel="canonical"[^>]*>\n', '', erro)
    erro = erro.replace('<h1>Django em português, do jeito que se usa no trabalho.</h1>',
                        '<h1>Página não encontrada</h1>\n    <p class="lead">Este endereço não existe mais. Procure a dica na busca acima ou escolha uma das mais recentes.</p>')
    (OUT / '404.html').write_text(erro, encoding='utf-8')
    hoje = datetime.date.today().isoformat()
    linhas = [f'<url><loc>{SITE_URL}/</loc><lastmod>{hoje}</lastmod></url>']
    for u, d in mapa:
        linhas.append(f'<url><loc>{u}</loc>' + (f'<lastmod>{d.isoformat()}</lastmod>' if d else '') + '</url>')
    (OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(linhas) + '\n</urlset>\n', encoding='utf-8')
    (OUT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n', encoding='utf-8')
    (OUT / '.nojekyll').write_text('', encoding='utf-8')
    print(f'{len(itens)} páginas geradas em {OUT}')


if __name__ == '__main__':
    main()
