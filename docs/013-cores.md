# Dica 13 - Cores

**Versões usadas no vídeo:** a dica não usa Django nem código; mostra cinco sites de paletas de cores (vídeo de julho de 2020).
{: .versoes }

<a href="https://youtu.be/EcwxPzgwE4I">
    <img src="../.gitbook/assets/youtube.png">
</a>

Escolher as cores do seu site é uma das partes mais difíceis de montar um template. Nesta dica vamos ver cinco sites que ajudam a montar uma paleta de cores e já entregam os códigos (hexadecimal, RGB, HSL) prontos para usar no CSS do seu projeto.

[color.adobe.com/pt/create/color-wheel](https://color.adobe.com/pt/create/color-wheel)

[coolors.co](https://coolors.co/)

[materialuicolors.co](https://materialuicolors.co/)

[htmlcolorcodes.com](https://htmlcolorcodes.com/)

[clrs.cc](http://clrs.cc/)

## Adobe Color

Em [color.adobe.com/pt/create/color-wheel](https://color.adobe.com/pt/create/color-wheel) você tem uma roda de cores (aba **Disco de cores**). À esquerda escolhe a regra de harmonia:

* Análogo
* Monocromático
* Tríade
* Complementar
* Dividir complementar
* Dividir complementar duas vezes
* Quadrado
* Composto
* Sombras
* Personalizado

Ao trocar a regra, ou arrastar os pontos na roda, a paleta de cinco cores logo abaixo muda junto. Cada cor aparece com o seu código hexadecimal (por exemplo `#326602`, `#9BEA4B`) e com os controles de R, G e B para fazer o ajuste fino.

## Coolors

Em [coolors.co](https://coolors.co/):

* **Generate**: gera uma paleta aleatória. Cada vez que você aperta a barra de espaço, sai uma paleta nova. No vídeo saiu `264653`, `2A9D8F`, `E9C46A`, `F4A261`.
* **Explore**: mostra paletas prontas (as mais populares, em "Trending"). No menu `...` de uma paleta, a opção **Open in the generator** abre essa paleta no gerador, onde você pode ajustar cada cor e ver os valores em hexadecimal e RGB.

## Material UI Colors

Em [materialuicolors.co](https://materialuicolors.co/) as cores são fixas: é a paleta do Material Design (Red, Pink, Purple, Deep Purple, Indigo, Blue, Light Blue, Cyan, Teal, Green, Light Green, Lime, Yellow, Amber, Orange, Deep Orange, Brown, Grey, Blue Grey).

* O controle **Level** no topo muda a intensidade (o padrão é 500; no vídeo ele passou para 600), deixando todas as cores mais claras ou mais escuras.
* O formato do código (por exemplo `HEX - #1234EF`) também é escolhido no topo.
* Clicando numa cor (**Copy**), o código já vai para a área de transferência.

## HTML Color Codes

Em [htmlcolorcodes.com](https://htmlcolorcodes.com/) há:

* **Picker**: um seletor de cor. Você escolhe a cor e ele mostra os valores em HEX, RGB e HSL (por exemplo `#19238C`, `25, 35, 140`, `235, 82%, 32%`) e ainda sugere uma paleta que combina com ela.
* **Chart**: tabelas de cores prontas, como a Flat Design Color Chart, a do Google Material Design e a Web Safe Color Chart (as 216 cores "seguras" da web antiga).
* **Names**: os nomes de cores do HTML (`IndianRed`, `LightCoral` etc.) com o código de cada um.

## Clrs

Em [clrs.cc](http://clrs.cc/) há uma paleta pré-definida, pensada para substituir as cores padrão do navegador ("The New Defaults" em vez de "The Old Defaults"): `navy #001f3f`, `blue #0074D9`, `aqua #7FDBFF`, `teal #39CCCC`, `olive #3D9970`, `green #2ECC40`, `lime #01FF70`, `orange #FF851B`, `maroon #85144b`, `fuchsia #F012BE`, `purple #B10DC9`, `black #111111`, `gray #AAAAAA`, `silver #DDDDDD`. O site também oferece um arquivo `colors.css` com classes prontas para aplicar essas cores em fundo, texto e borda.

## Usando a paleta no projeto

Escolhida a paleta, basta copiar os códigos para o CSS do seu projeto. Por exemplo, com a paleta gerada no Coolors:

```css
/* core/static/css/style.css */
:root {
  --cor-primaria: #264653;
  --cor-secundaria: #2A9D8F;
  --cor-destaque: #E9C46A;
  --cor-alerta: #F4A261;
}

.navbar {
  background-color: var(--cor-primaria);
}
```

Como carregar esse arquivo estático no template é assunto da [Dica 14 - Herança de templates e arquivos estáticos](014-heranca-de-templates-e-arquivos-estaticos.md).

Com esses sites fica bem mais fácil deixar o seu site mais colorido e bonito.
