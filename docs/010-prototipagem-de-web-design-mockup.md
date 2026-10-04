# Dica 10 - Prototipagem de web design (Mockup)

**Versões usadas no vídeo:** não usa Django nem código; são ferramentas on-line, mostradas como estavam em junho de 2020.
{: .versoes }

<a href="https://youtu.be/Ypbj_d1oGuY">
    <img src="../.gitbook/assets/youtube.png">
</a>

Antes de escrever o HTML das páginas de um projeto Django, vale a pena desenhar como elas vão ficar. Esse esboço é o **mockup** (ou *wireframe*), e o processo é chamado de prototipagem de web design. É o mesmo rascunho que você faria com papel e caneta junto com o cliente, só que numa ferramenta on-line, fácil de alterar, exportar e compartilhar.

O vídeo apresenta cinco ferramentas on-line para isso. Todas têm um plano gratuito (algumas com limites) e as que pedem cadastro aceitam login com a conta do Google.

## 1. Excalidraw

[excalidraw.com](https://excalidraw.com/)

* **Não precisa de login**: é só abrir o site e desenhar. O navegador guarda o último desenho que você fez.
* Tem retângulo, losango, elipse, seta, linha, desenho livre e texto. Na seta, você pode clicar em vários pontos para fazer curvas e apertar **Enter** para terminar.
* Para cada forma dá para escolher a cor do traço e do fundo, o preenchimento (**Hachure**, **Cross-hatch** ou **Solid**), a espessura e o estilo da linha.
* O traço tem um estilo de desenho à mão, ótimo para rascunhos.
* Em **Export** você salva em **PNG** ou **SVG**, inclusive com resolução maior. Se houver elementos selecionados, ele exporta só a seleção.

No vídeo, o exemplo aberto no Excalidraw é um diagrama do "T" do MTV (os templates) de um projeto Django: um `base.html` com `head` (e o `style.css`), `nav.html`, `content`, `footer.html` e `main.js`, e os templates `list.html`, `detail.html` e `form.html` que estendem a base.

## 2. Moqups

[moqups.com](https://moqups.com/)

* Precisa de login (dá para entrar com a conta do Google). Tem planos pagos, mas a versão gratuita já permite desenhar bastante.
* Você cria um projeto (por exemplo, **Blank Project**) e arrasta os componentes da barra lateral: campos de texto, área de texto, data, botões, checkbox, rádio, combo box, tabelas, imagens etc.
* É bom para desenhar telas de sistema, como um formulário com botão **Save** e uma tabela com uma coluna de ações (**Edit**).
* A exportação fica no plano pago.

## 3. Balsamiq

[balsamiq.com](https://balsamiq.com/)

* No site, vá em **Log In** e escolha **Balsamiq Cloud** (a versão web, em [balsamiq.cloud](https://balsamiq.cloud/)). Dá para entrar com a conta do Google.
* Também tem estilo de desenho à mão.
* Tem muitos componentes prontos: a janela do navegador (*browser*), acordeão, calendário, botões, texto de várias linhas e muito mais. É só arrastar e escrever.

## 4. Marvel

[marvelapp.com](https://marvelapp.com/)

* Tem planos pagos e um plano gratuito. Na época do vídeo, o plano gratuito permitia **um projeto só**: para criar outro, foi preciso apagar o projeto antigo (o Marvel pede para digitar `DELETE` para confirmar).
* Para começar, clique em **Create project**, dê um nome, escolha o tipo (por exemplo **Website/TV**) e crie o projeto.
* Dentro do projeto você pode enviar imagens das telas ou desenhar com as ferramentas de retângulo, elipse, linha e texto.
* Também serve para montar protótipos navegáveis, ligando uma tela a outra.

## 5. MockFlow

[mockflow.com](https://www.mockflow.com/)

* Precisa de cadastro (também aceita a conta do Google). Você cria um *wireframe* e arrasta os componentes para a página.
* A biblioteca de componentes **Sketchy Handdrawn UI** dá o estilo de desenho à mão. No vídeo foram usados botões, a imagem de perfil de usuário, uma lista de *checkbox* e um bloco de texto.
* Depois de editar, clique em **Save Changes** para salvar.

## Conclusão

Com qualquer uma dessas ferramentas você monta o layout das páginas antes de escrever o HTML. Para rascunhos rápidos, sem cadastro, o Excalidraw é o mais prático; para telas de sistema, com formulários e tabelas, o Moqups, o Balsamiq e o MockFlow têm mais componentes prontos. Depois do mockup, o próximo passo é escolher um framework CSS para montar as páginas, assunto da [Dica 11](011-bootstrap-e-bulma--colorlib.md).
