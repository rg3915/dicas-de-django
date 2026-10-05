# Form Wizard com máquina de estados (JS)

Publicado em 23/12/2024.

**Testado com:** JavaScript puro e AlpineJS (só front-end, sem Django); o fim do tutorial mostra como ligar numa view Django.
{: .versoes }

<a href="https://youtu.be/oqJxdjh6Iyk">
    <img src="../.gitbook/assets/youtube.png">
</a>

Um formulário wizard (em várias etapas) com uma **máquina de estados** para gerenciar o fluxo de etapas de forma previsível e escalável.

Github: [https://github.com/rg3915/form-wizard-state-machine](https://github.com/rg3915/form-wizard-state-machine)

Formulários longos assustam o usuário. A solução comum é quebrá-los em etapas, mas aí surge outro problema: controlar qual etapa aparece, como avançar, como voltar e quais etapas já foram concluídas. Quando isso é feito com uma pilha de variáveis booleanas (`mostraEtapa2`, `mostraEtapa3`...), o código vira um emaranhado.

Neste tutorial vamos montar um cadastro de pessoa física ou jurídica em cinco etapas, usando uma máquina de estados escrita em JavaScript puro e ligada à tela com AlpineJS. O projeto é só front-end: não há Django nem backend. No fim, comento como plugar isso numa view Django.

## O que é uma máquina de estados

Uma máquina de estados organiza a lógica de um sistema em **estados finitos**. O sistema está em **um único estado por vez**, cada estado define o que é exibido e quais transições são permitidas para outros estados.

No nosso caso:

* os estados são as etapas: `inicio`, `identificacao`, `documentos`, `endereco` e `confirmacao`;
* existe um único `currentState`;
* as transições são `nextState` (avançar), `prevState` (voltar) e `setState` (ir direto para um estado).

## O fluxo

1. **Início**: o usuário escolhe pessoa física ou jurídica.
2. **Identificação**: nome e e-mail.
3. **Documentos**: RG e CPF, se for pessoa física; CNPJ e razão social, se for jurídica.
4. **Endereço**: CEP (com preenchimento automático pela API do ViaCEP), logradouro, complemento, bairro, cidade e UF.
5. **Confirmação**: mostra todos os dados para revisão e finaliza o cadastro.

O repositório traz esse fluxo descrito como diagrama Mermaid:

```
%% stateDiagram.mermaid
stateDiagram-v2
    [*] --> Inicio

    state Inicio {
        [*] --> EscolhaTipo
        EscolhaTipo --> PessoaFisica : Seleciona PF
        EscolhaTipo --> PessoaJuridica : Seleciona PJ
    }
    %% ... (veja o arquivo completo no GitHub)

    Inicio --> Identificacao : Após escolha do tipo

    Identificacao --> Documentos : Próximo
    Documentos --> Identificacao : Anterior

    Documentos --> Endereco : Próximo
    Endereco --> Documentos : Anterior

    Endereco --> Confirmacao : Próximo
    Confirmacao --> Endereco : Anterior

    Confirmacao --> [*] : Finalizar Cadastro
```

Código completo: [stateDiagram.mermaid](https://github.com/rg3915/form-wizard-state-machine/blob/af7542d8b730766440da42f10ef0029e5bc6d9c2/stateDiagram.mermaid)

Cole esse conteúdo em [https://mermaid.live/](https://mermaid.live/) para ver o desenho. Desenhar o diagrama antes do código é a melhor parte do padrão: o código passa a ser uma tradução direta dele.

## Pré-requisitos

* Noções de HTML e JavaScript.
* Um servidor HTTP estático qualquer (o Python já traz um).
* Conexão com a internet: Pico CSS e AlpineJS vêm de CDN, e o CEP é consultado no ViaCEP.

## Estrutura

```
form-wizard-state-machine/
├── assets/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── index.html
└── stateDiagram.mermaid
```

## A máquina de estados em JavaScript

Toda a lógica fica numa função `formWizard()` que devolve um objeto. O AlpineJS usa esse objeto como estado reativo do componente (`x-data="formWizard()"`).

```javascript
// assets/js/main.js
const formWizard = () => ({
  // Estados possíveis do formulário
  states: ['inicio', 'identificacao', 'documentos', 'endereco', 'confirmacao'],
  currentState: 'inicio',
  tipo: null,
  /* ... (toast e form: veja o arquivo completo no GitHub) */

  resetForm() {
    this.form = {
      nome: '',
      email: '',
      cpf: '',
      rg: '',
      cnpj: '',
      razaoSocial: '',
      cep: '',
      logradouro: '',
      complemento: '',
      cidade: '',
      uf: ''
    }
    this.tipo = null
  },

  // Define um estado específico
  setState(state) {
    if (this.states.includes(state)) {
      this.currentState = state
    }
  },

  // Define o tipo de cadastro e inicia o fluxo
  selectTipo(tipo) {
    this.tipo = tipo
    this.setState('identificacao')
  },
  /* ... */

  // Avança para o próximo estado
  nextState() {
    // Obtém o índice do estado atual
    const currentIndex = this.states.indexOf(this.currentState)

    // Verifica se não é o último estado
    if (currentIndex < this.states.length - 1) {
      // Avança para o próximo estado
      this.currentState = this.states[currentIndex + 1]
    }
  },
  /* ... (veja o arquivo completo no GitHub) */
})
```

Código completo: [assets/js/main.js](https://github.com/rg3915/form-wizard-state-machine/blob/af7542d8b730766440da42f10ef0029e5bc6d9c2/assets/js/main.js)

Vamos por partes.

### Os dados

* `states` é a lista ordenada dos estados. A **ordem do array é a ordem do fluxo**: todas as transições são calculadas a partir dos índices.
* `currentState` começa em `'inicio'`.
* `tipo` guarda `'fisica'` ou `'juridica'` e decide quais campos aparecem em Documentos.
* `toast` guarda o estado da notificação (mensagem, visibilidade, animação de saída, tipo e o id do `setTimeout`).
* `form` concentra todos os campos de todas as etapas. Como o objeto é um só, nada se perde quando o usuário volta ou avança.

### As transições

* **`setState(state)`** vai direto para um estado, mas só se ele existir em `states`. Essa guarda impede estados inválidos, por exemplo um erro de digitação no HTML.
* **`selectTipo(tipo)`** é a transição de saída do `inicio`: grava o tipo e vai para `identificacao`.
* **`nextState()`** pega o índice atual e, se não for o último, passa para o seguinte.
* **`prevState()`** faz o inverso, sem passar do primeiro.
* **`hasPassedState(state)`** responde se um estado já ficou para trás (índice menor que o atual). É usado para pintar as etapas concluídas na barra de progresso.

Para acrescentar uma etapa nova, basta incluir o nome no array `states` na posição certa e criar a `<section>` correspondente no HTML. Nenhum método precisa mudar.

### Envio e toast

`handleSubmit()` é chamado no estado `confirmacao`. Aqui ele só mostra os dados no console, exibe o toast de sucesso, limpa o formulário e volta ao `inicio`. `showToast()` cancela um toast anterior, mostra o novo e agenda o `hideToast()` para 3 segundos depois; `hideToast()` liga a classe `removing` (animação de saída) e só esconde de fato após 300 ms, o tempo da transição CSS.

### Busca de CEP

`getAddressByCep()` aceita CEP com 8 dígitos ou com hífen (9 caracteres), consulta `https://viacep.com.br/ws/<cep>/json/` com `fetch` e preenche logradouro, bairro, cidade (`localidade` na resposta) e UF.

## O HTML com AlpineJS

```html
<!-- index.html -->
<!-- ... -->
<body>
  <div class="container" x-data="formWizard()">
    <!-- ... -->
    <!-- START Navegação -->
    <nav x-show="currentState !== 'inicio'">
      <ul>
        <li :class="{
          'active': currentState === 'identificacao',
          'completed': hasPassedState('identificacao')
        }">Identificação</li>
        <!-- ... -->
      </ul>
    </nav>
    <!-- END Navegação -->

    <form @submit.prevent="handleSubmit">
      <!-- START Estado: Identificação -->
      <section x-show="currentState === 'identificacao'">
        <fieldset>
          <h2>Identificação</h2>
          <label class="required">Nome:</label>
          <input type="text" x-model="form.nome" required>
          <label class="required">E-mail:</label>
          <input type="email" x-model="form.email" required>
          <div class="buttons">
            <button type="button" @click="setState('inicio')">Anterior</button>
            <button type="button" @click="nextState">Próximo</button>
          </div>
        </fieldset>
      </section>
      <!-- END Estado: Identificação -->
      <!-- ... (veja o arquivo completo no GitHub) -->
    </form>
  </div>
<!-- ... -->
```

Código completo: [index.html](https://github.com/rg3915/form-wizard-state-machine/blob/af7542d8b730766440da42f10ef0029e5bc6d9c2/index.html)

No repositório os atributos estão um por linha; aqui juntei alguns na mesma linha para encurtar, sem mudar nada.

Como o HTML conversa com a máquina:

* **`x-data="formWizard()"`** cria o componente com o objeto de `main.js`. O script `main.js` é carregado no fim do `body`, e o AlpineJS (com `defer`) só inicializa depois que o documento foi lido, por isso `formWizard` já existe quando o Alpine procura por ela.
* **`x-show="currentState === '...'"`** em cada `<section>`: só a etapa do estado atual fica visível. Esta é a regra central: a tela é uma função do estado.
* **`<template x-if="tipo === 'fisica'">`** em Documentos e na Confirmação: aqui é `x-if` (e não `x-show`) porque os campos do outro tipo nem precisam existir no DOM.
* **`:class` na `<nav>`**: a etapa atual recebe `active` e as anteriores recebem `completed`, via `hasPassedState`.
* **Botões de navegação** são `type="button"` para não enviarem o formulário. Só o "Finalizar Cadastro", na confirmação, é `type="submit"`, e o `@submit.prevent="handleSubmit"` evita o recarregamento da página.
* **`x-model`** liga cada campo a `form`, e o `@change` do CEP dispara a busca no ViaCEP.

## O CSS

O Pico CSS cuida da aparência geral. O `style.css` faz a barra de etapas (círculos ligados por uma linha), os botões e o toast:

```css
/* assets/css/style.css */
/* ... */

nav ul li::before {
  content: '';
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid #e0e0e0;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

nav ul li.active::before {
  border-color: #1095c1;
  background: #1095c1;
  box-shadow: 0 0 0 3px rgba(16, 149, 193, 0.2);
}

nav ul li.completed::before {
  border-color: #1095c1;
  background: #1095c1;
}
/* ... (veja o arquivo completo no GitHub) */
```

Código completo: [assets/css/style.css](https://github.com/rg3915/form-wizard-state-machine/blob/af7542d8b730766440da42f10ef0029e5bc6d9c2/assets/css/style.css)

O truque da barra de etapas: cada `li::before` desenha um círculo cinza; as classes `active` e `completed` pintam o círculo de azul, e o `transition` anima a troca.

## Rodando

```bash
git clone https://github.com/rg3915/form-wizard-state-machine.git
cd form-wizard-state-machine

python -m http.server
```

Acesse `http://localhost:8000`, escolha Pessoa Física, preencha nome e e-mail, avance, preencha os documentos, digite um CEP (por exemplo `01001000`) e saia do campo para ver o endereço preenchido. Na confirmação, clique em "Finalizar Cadastro": o toast aparece, os dados vão para o console do navegador e o wizard volta ao início.

## Pontos de atenção e melhorias

O código acima é o do repositório. Ao estudá-lo, repare em três detalhes:

* **`resetForm()` não limpa o `bairro`**: o campo ficou de fora do objeto recriado. Acrescente `bairro: ''` para o reset ficar completo.
* **Não há validação por etapa**: o `required` em nome e e-mail só é checado pelo navegador no submit final, porque os botões "Próximo" são `type="button"`. Uma forma de validar sem quebrar o padrão é colocar uma guarda na transição, algo como um método `canAdvance()` consultado dentro de `nextState()` antes de trocar o estado. Isso não está no repositório; é uma sugestão de extensão.
* **Erros do ViaCEP**: CEP inexistente devolve `{"erro": true}` e os campos ficam `undefined`. Vale checar `data.erro` e chamar `showToast('CEP não encontrado', 'error')`.

## E o Django?

O projeto é só front-end, mas a integração é direta. Coloque o `index.html` como template, os arquivos de `assets/` em `static/` (usando `{% static %}` nos links) e, em `handleSubmit()`, troque o `console.log` por um `fetch` com `POST` para uma view ou endpoint de API que receba `{ tipo, dados }`, lembrando de enviar o cabeçalho `X-CSRFToken`. A máquina de estados continua igual: ela só controla a navegação entre etapas.

## Resumo

* Modele as etapas como uma lista ordenada de estados e mantenha um único `currentState`.
* Centralize as transições em `nextState`, `prevState` e `setState`, com guardas simples.
* Faça a tela depender só do estado (`x-show`, `x-if`, `:class`).
* Para crescer, acrescente estados ao array; a lógica de navegação não muda.

Para ler mais sobre o padrão: [https://refactoring.guru/pt-br/design-patterns/state](https://refactoring.guru/pt-br/design-patterns/state)
