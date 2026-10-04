# Dica 11 - Bootstrap e Bulma + Colorlib

**Versões usadas no vídeo:** não usa Django; mostra o Bootstrap 4.5 e o Bulma 0.9.0, como estavam em junho de 2020.
{: .versoes }

<a href="https://youtu.be/J86_rp0ibGI">
    <img src="../.gitbook/assets/youtube.png">
</a>

Depois de desenhar o mockup das páginas (veja a [Dica 10](010-prototipagem-de-web-design-mockup.md)), você precisa montar o HTML e o CSS. Em vez de começar do zero, dá para usar um **framework CSS**, com componentes prontos e responsivos, e partir de um **template** pronto. Esta dica apresenta dois frameworks CSS bem conhecidos, o Bootstrap e o Bulma, e alguns sites com templates gratuitos para eles, além do Colorlib.

## Bootstrap

[getbootstrap.com](https://getbootstrap.com/)

O Bootstrap é o framework CSS mais usado. A versão do vídeo é a 4.5 (Bootstrap 4, que usa jQuery e Popper.js no JavaScript).

### Exemplos (templates) do Bootstrap

[getbootstrap.com/docs/4.5/examples](https://getbootstrap.com/docs/4.5/examples/)

Na página **Examples** há vários modelos de página prontos, feitos só com o Bootstrap, para você usar como ponto de partida. Alguns deles:

* **Album**: página simples para galerias de fotos, portfólios etc.
* **Pricing**: página de preços feita com *cards*.
* **Checkout**: formulário de compra com validação.
* **Product**: página de marketing de um produto.
* **Dashboard**: painel administrativo com barra lateral.

Para usar um exemplo, abra-o no navegador e veja o código-fonte, ou baixe todos de uma vez: no topo da página **Examples**, clique em **Download examples**. Ele baixa o código-fonte do Bootstrap com a pasta de exemplos.

Não confunda com o botão **Download** do menu, que leva à página de download do próprio Bootstrap (o CSS e o JavaScript compilados, na versão 4.5.0).

## Bulma

[bulma.io](https://bulma.io/)

O Bulma é outro framework CSS. Ele é só CSS (não traz JavaScript) e as classes têm nomes fáceis de ler, como `button`, `card`, `columns`, `is-primary`.

Na **Documentation** você encontra:

* **Overview > Start**: as formas de instalar o Bulma.
  1. Pelo npm (recomendado): `npm install bulma`.
  2. Pelo CDN do [jsDelivr](https://www.jsdelivr.com/package/npm/bulma), colocando o CSS direto no `<head>` do HTML.
  3. Baixando o CSS do repositório no GitHub.
  
  A documentação lembra que, para usar ícones com o Bulma, você precisa incluir o Font Awesome.
* **Components**: todos os componentes, com exemplos de código. No vídeo foi aberto o **Card**, formado por elementos que você combina: `card` (o container principal), `card-header` (com `card-header-title` e `card-header-icon`), `card-image`, `card-content` e `card-footer` (com os itens `card-footer-item`).

### Templates para o Bulma

* [bulmatemplates.github.io/bulma-templates](https://bulmatemplates.github.io/bulma-templates/): templates gratuitos, de licença livre, feitos com o Bulma (Admin, Band, Blog, Cards, Modal Cards, Neumorphic Login, Portfolio, Showcase, Registration Form, Tabs, Contact Page e outros). Cada um tem um botão **Preview**, para ver a página funcionando, e **Source Code**, para ver o código.
* [bulmathemes.com](https://bulmathemes.com/): mais temas para o Bulma, cada um com **Demo** e **Download**. Alguns são gratuitos (marcados como *FREE*) e outros são pagos.

## Colorlib

[colorlib.com](https://colorlib.com/)

O Colorlib tem muitos templates e temas, a maioria para WordPress, mas que também servem de inspiração ou de base para o HTML do seu projeto. Em **Free Themes** ficam os gratuitos (como Shapely, Unapp e Philosophy). Na página de cada tema há os botões **Demo**, para ver o tema funcionando, **Download** e **Documentation**. Nem todo tema tem download direto; nesse caso, escolha outro.

## Conclusão

Com um framework CSS e um template pronto, você ganha tempo para montar as páginas do seu projeto Django: basta adaptar o HTML do template para os templates do Django (`base.html`, `{% block content %}` etc.). Escolha o que mais combina com o seu gosto: o Bootstrap, mais popular e com mais material disponível, ou o Bulma, mais simples e só CSS.

Observação: o Bootstrap atual é a versão 5, que não depende mais do jQuery. Os links acima são da versão 4.5, a mostrada no vídeo.
