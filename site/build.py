"""Gera o site estático do Dicas de Django a partir de SUMMARY.md e docs/*.md.

Uso:
    python site/build.py            # gera em _site/
    python site/build.py --base /dicas-de-django/

Dependências: markdown, pygments.
"""
import html
import json
import re
import shutil
import sys
from pathlib import Path

import markdown
from pygments.formatters import HtmlFormatter

ROOT = Path(__file__).resolve().parent.parent
THEME = ROOT / 'site' / 'theme'
OUT = ROOT / '_site'
REPO_URL = 'https://github.com/rg3915/dicas-de-django'
YOUTUBE_URL = 'https://www.youtube.com/@RegisdoPython'

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


def nesta_pagina(toc):
    links = []
    for t in toc:
        for h2 in t.get('children', []) if t['level'] == 1 else [t]:
            if h2['level'] == 2:
                links.append(f'<a href="#{h2["id"]}">{html.escape(html.unescape(h2["name"]))}</a>')
    if not links:
        return ''
    return '<nav class="toc" aria-label="Nesta página"><p>Nesta página</p>' + ''.join(links) + '</nav>'


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
        if f.suffix in ('.css', '.js', '.svg', '.png'):
            shutil.copy(f, OUT / 'assets' / f.name)
    # cores do código (Pygments) para os dois temas
    claro = HtmlFormatter(style='friendly').get_style_defs('.hl')
    escuro = HtmlFormatter(style='github-dark').get_style_defs('.hl')
    escuro = '\n'.join(f':root[data-theme="dark"] {linha}' if linha.startswith('.hl') else linha for linha in escuro.splitlines())
    (OUT / 'assets' / 'code.css').write_text(claro + '\n' + escuro, encoding='utf-8')

    busca = []
    for n, it in enumerate(itens):
        bruto = preparar_markdown(it['arquivo'].read_text(encoding='utf-8'))
        corpo, toc = renderizar(bruto)
        corpo, h1 = tirar_h1(corpo)
        titulo = h1 or it['nome']
        ant = itens[n - 1] if n > 0 else None
        prox = itens[n + 1] if n + 1 < len(itens) else None
        navega = '<nav class="vizinhos">'
        navega += f'<a href="../{ant["slug"]}/" rel="prev"><small>Anterior</small>{html.escape(ant["nome"])}</a>' if ant else '<span></span>'
        navega += f'<a href="../{prox["slug"]}/" rel="next"><small>Próxima</small>{html.escape(prox["nome"])}</a>' if prox else '<span></span>'
        navega += '</nav>'
        valores = {
            '{{titulo_pagina}}': html.escape(f'{titulo} | Dicas de Django'),
            '{{descricao}}': html.escape(texto_puro(corpo)[:160].strip()),
            '{{lateral}}': lateral(itens, it['slug']),
            '{{numero}}': html.escape(it['numero']),
            '{{numero_classe}}': '' if it['numero'] else ' sem-numero',
            '{{titulo}}': html.escape(titulo),
            '{{secao}}': html.escape(it['secao']),
            '{{minutos}}': str(minutos(corpo)),
            '{{corpo}}': corpo,
            '{{toc}}': nesta_pagina(toc),
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
    home = preencher(home, {
        '{{lateral}}': lateral(itens, None).replace('href="../', 'href="'),
        '{{recentes}}': cards,
        '{{total}}': str(len([i for i in itens if i['numero']])),
        '{{raiz}}': '',
        '{{youtube}}': YOUTUBE_URL,
        '{{repo}}': REPO_URL,
        '{{base}}': base,
    })
    (OUT / 'index.html').write_text(home, encoding='utf-8')
    (OUT / '404.html').write_text(home, encoding='utf-8')
    (OUT / '.nojekyll').write_text('', encoding='utf-8')
    print(f'{len(itens)} páginas geradas em {OUT}')


if __name__ == '__main__':
    main()
