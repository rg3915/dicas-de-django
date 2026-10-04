# Dica 12 - Imagens: pexels e unsplash

**Versões usadas no vídeo:** a dica não usa Django nem código; mostra dois sites de imagens gratuitas (vídeo de julho de 2020).
{: .versoes }

<a href="https://youtu.be/g95YG5RGGmE">
    <img src="../.gitbook/assets/youtube.png">
</a>

Quando estamos montando o template de um projeto Django (uma landing page, a tela de login, um card de produto), quase sempre falta uma imagem de boa qualidade para preencher o layout. Nesta dica vamos ver dois sites que oferecem fotos gratuitas, em alta resolução, que você pode baixar e usar no seu projeto:

[pexels.com](https://www.pexels.com/pt-br/)

[unsplash.com](https://unsplash.com/)

## Pexels

1. Acesse [pexels.com](https://www.pexels.com/pt-br/). A página inicial já mostra "As melhores fotos gratuitas" e algumas coleções.
2. Digite um termo na busca (**Buscar fotos grátis**). No vídeo, a busca foi por `tower`, que trouxe várias fotos de prédios e torres, e depois por `computer`, que trouxe fotos de notebooks, mesas de trabalho e telas com código.
3. Clique na imagem escolhida e faça o download. O download é gratuito.

## Unsplash

1. Acesse [unsplash.com](https://unsplash.com/) e use a busca (**Search free high-resolution photos**) ou navegue pelas categorias do topo (Nature, Wallpapers, Technology etc.).
2. Clique na foto e depois em **Download free**.
3. Depois do download, o Unsplash abre um aviso **Say thanks** pedindo que você dê o crédito ao fotógrafo, com um texto pronto para copiar. No vídeo, a foto baixada foi a de um prédio colorido, e o texto era:

```
Photo by Amirul Muiz on Unsplash
```

O texto copiado já vem com os links para o perfil do fotógrafo e para o Unsplash. Se quiser colocar o crédito no seu template, ele fica mais ou menos assim (troque o nome e os links pelos da foto que você baixou):

```html
<!-- templates/index.html -->
<span>
  Photo by <a href="https://unsplash.com/@usuario-do-fotografo">Nome do Fotógrafo</a>
  on <a href="https://unsplash.com/">Unsplash</a>
</span>
```

Dar o crédito é uma recomendação dos sites, mas, independente disso, as imagens são gratuitas.

## Usando a imagem no projeto

Baixada a imagem, coloque o arquivo na pasta de arquivos estáticos do seu app (por exemplo `core/static/img/`) e use a tag `{% static %}` no template. Isso é explicado na [Dica 14 - Herança de templates e arquivos estáticos](014-heranca-de-templates-e-arquivos-estaticos.md).

Pronto: dois sites para escolher imagens à vontade para os seus templates.
