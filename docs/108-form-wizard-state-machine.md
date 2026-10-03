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

    state Identificacao {
        [*] --> DadosBasicos
        state DadosBasicos {
            Nome
            Email
        }
    }

    state Documentos {
        state DocumentosPF {
            CPF
            RG
        }

        state DocumentosPJ {
            CNPJ
            RazaoSocial
        }
    }

    state Endereco {
        [*] --> DadosEndereco
        state DadosEndereco {
            CEP
            Logradouro
            Complemento
            Cidade
            UF
        }
    }

    state Confirmacao {
        state ExibeDados {
            DadosPessoais
            DadosDocumentos
            DadosEndereço
        }
    }

    Inicio --> Identificacao : Após escolha do tipo

    Identificacao --> Documentos : Próximo
    Documentos --> Identificacao : Anterior

    Documentos --> Endereco : Próximo
    Endereco --> Documentos : Anterior

    Endereco --> Confirmacao : Próximo
    Confirmacao --> Endereco : Anterior

    Confirmacao --> [*] : Finalizar Cadastro

    note right of Documentos
        Se PF: Mostra DocumentosPF
        Se PJ: Mostra DocumentosPJ
    end note

    note right of Confirmacao
        Exibe todos os dados
        preenchidos para revisão
        final
    end note
```

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
  // Adiciona estado para o toast
  toast: {
    message: '',
    visible: false,
    removing: false,
    type: 'success',
    timeoutId: null
  },
  form: {
    nome: '',
    email: '',
    cpf: '',
    rg: '',
    cnpj: '',
    razaoSocial: '',
    cep: '',
    logradouro: '',
    complemento: '',
    bairro: '',
    cidade: '',
    uf: ''
  },

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

  // Verifica se já passou por determinado estado
  hasPassedState(state) {
    // Obtém o índice do estado atual no array
    const currentIndex = this.states.indexOf(this.currentState)

    // Obtém o índice do estado que queremos verificar
    const stateIndex = this.states.indexOf(state)

    // Retorna true se o estado verificado está antes do atual
    return stateIndex < currentIndex

  },

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

  // Retorna ao estado anterior
  prevState() {
    // Obtém o índice do estado atual
    const currentIndex = this.states.indexOf(this.currentState)

    // Verifica se não é o primeiro estado
    if (currentIndex > 0) {
      // Volta para o estado anterior
      this.currentState = this.states[currentIndex - 1]
    }
  },

  // Manipula o envio do formulário
  handleSubmit() {
    console.log('Formulário enviado:', {
      tipo: this.tipo,
      dados: this.form
    })
    this.showToast('Cadastro realizado com sucesso!')
    // Reset e retorno ao início
    this.resetForm()
    this.setState('inicio')
  },

  // Função para mostrar toast
  showToast(message, type = 'success') {
    // Limpa timeout anterior se existir
    if (this.toast.timeoutId) {
      clearTimeout(this.toast.timeoutId)
    }

    // Reset do estado do toast
    this.toast.removing = false
    this.toast.message = message
    this.toast.type = type
    this.toast.visible = true

    // Auto-hide após 3 segundos
    this.toast.timeoutId = setTimeout(() => {
      this.hideToast()
    }, 3000)
  },

  // Função para esconder toast com animação
  hideToast() {
    this.toast.removing = true

    // Aguarda a animação terminar antes de esconder
    setTimeout(() => {
      this.toast.visible = false
      this.toast.removing = false
    }, 300)

    // Limpa o timeout se existir
    if (this.toast.timeoutId) {
      clearTimeout(this.toast.timeoutId)
    }
  },

  // Função para pesquisar o CEP no viacep
  getAddressByCep(cep) {
    if (cep.length !== 8 && cep.length !== 9) {
      return Promise.reject(new Error('Invalid CEP length'))
    }

    return fetch(`https://viacep.com.br/ws/${cep}/json/`)
      .then(response => response.json())
      .then(data => {
        // Update input fields
        this.form.logradouro = data.logradouro
        this.form.bairro = data.bairro
        this.form.cidade = data.localidade
        this.form.uf = data.uf

        console.log('Address updated:', data)
      })
      .catch(error => {
        console.error(error.message)
      })
  },

})
```

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
<!DOCTYPE html>
<html lang="pt-BR">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="https://picocss.com/favicon.svg" type="image/svg+xml">

  <title>Form Wizard - Máquina de Estado</title>

  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css" />
  <link rel="stylesheet" href="assets/css/style.css">

  <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.12.0/dist/cdn.min.js"></script>
</head>

<body>
  <div class="container" x-data="formWizard()">
    <!-- START Toast container -->
    <div class="toast-container">
      <div
        class="toast"
        :class="{
          'visible': toast.visible,
          'removing': toast.removing,
          'success': toast.type === 'success',
          'error': toast.type === 'error'
        }"
        @click="hideToast"
        x-show="toast.visible"
      >
        <span x-text="toast.message"></span>
        <span class="toast-close">×</span>
      </div>
    </div>
    <!-- END Toast container -->

    <header>
      <h1>Cadastro de Pessoa</h1>
    </header>

    <!-- START Seleção do tipo de cadastro -->
    <section class="tipo-cadastro" x-show="currentState === 'inicio'">
      <button @click="selectTipo('fisica')" :class="{ 'outline': tipo !== 'fisica' }">
        Pessoa Física
      </button>
      <button @click="selectTipo('juridica')" :class="{ 'outline': tipo !== 'juridica' }">
        Pessoa Jurídica
      </button>
    </section>
    <!-- END Seleção do tipo de cadastro -->

    <!-- START Navegação -->
    <nav x-show="currentState !== 'inicio'">
      <ul>
        <li :class="{
          'active': currentState === 'identificacao',
          'completed': hasPassedState('identificacao')
        }">Identificação</li>
        <li :class="{
          'active': currentState === 'documentos',
          'completed': hasPassedState('documentos')
        }">Documentos</li>
        <li :class="{
          'active': currentState === 'endereco',
          'completed': hasPassedState('endereco')
        }">Endereço</li>
        <li :class="{
          'active': currentState === 'confirmacao',
          'completed': hasPassedState('confirmacao')
        }">Confirmação</li>
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

      <!-- START Estado: Documentos -->
      <section x-show="currentState === 'documentos'">
        <h2>Documentos</h2>
        <template x-if="tipo === 'fisica'">
          <fieldset>
            <label>CPF:
              <input type="text" x-model="form.cpf">
            </label>
            <label>
              RG:
              <input type="text" x-model="form.rg">
            </label>
          </fieldset>
        </template>
        <template x-if="tipo === 'juridica'">
          <fieldset>
            <label>
              CNPJ:
              <input type="text" x-model="form.cnpj">
            </label>
            <label>
              Razão Social:
              <input type="text" x-model="form.razaoSocial">
            </label>
          </fieldset>
        </template>

        <div class="buttons">
          <button type="button" @click="prevState">Anterior</button>
          <button type="button" @click="nextState">Próximo</button>
        </div>
      </section>
      <!-- END Estado: Documentos -->

      <!-- START Estado: Endereço -->
      <section x-show="currentState === 'endereco'">
        <fieldset>
          <h2>Endereço</h2>
          <label>
            CEP:
            <input type="text" x-model="form.cep" @change="getAddressByCep(form.cep)">
          </label>
          <label>
            Logradouro:
            <input type="text" x-model="form.logradouro">
          </label>
          <label>
            Complemento:
            <input type="text" x-model="form.complemento">
          </label>
          <label>
            Bairro:
            <input type="text" x-model="form.bairro">
          </label>
          <label>
            Cidade:
            <input type="text" x-model="form.cidade">
          </label>
          <label>
            UF:
            <input type="text" x-model="form.uf">
          </label>
          <div class="buttons">
            <button type="button" @click="prevState">Anterior</button>
            <button type="button" @click="nextState">Próximo</button>
          </div>
        </fieldset>
      </section>
      <!-- END Estado: Endereço -->

      <!-- START Estado: Confirmação -->
      <section x-show="currentState === 'confirmacao'">
        <h2>Confirmação dos Dados</h2>
        <div>
          <h3>Dados Pessoais</h3>
          <p><strong>Nome:</strong> <span x-text="form.nome"></span></p>
          <p><strong>Email:</strong> <span x-text="form.email"></span></p>

          <template x-if="tipo === 'fisica'">
            <div>
              <p><strong>CPF:</strong> <span x-text="form.cpf"></span></p>
              <p><strong>RG:</strong> <span x-text="form.rg"></span></p>
            </div>
          </template>

          <template x-if="tipo === 'juridica'">
            <div>
              <p><strong>CNPJ:</strong> <span x-text="form.cnpj"></span></p>
              <p><strong>Razão Social:</strong> <span x-text="form.razaoSocial"></span></p>
            </div>
          </template>

          <h3>Endereço</h3>
          <p><strong>CEP:</strong> <span x-text="form.cep"></span></p>
          <p><strong>Logradouro:</strong> <span x-text="form.logradouro"></span></p>
          <p><strong>Complemento:</strong> <span x-text="form.complemento || '---'"></span></p>
          <p><strong>Bairro:</strong> <span x-text="form.bairro"></span></p>
          <p><strong>Cidade:</strong> <span x-text="form.cidade"></span></p>
          <p><strong>UF:</strong> <span x-text="form.uf"></span></p>
        </div>
        <div class="buttons">
          <button type="button" @click="prevState">Anterior</button>
          <button type="submit">Finalizar Cadastro</button>
        </div>
      </section>
      <!-- END Estado: Confirmação -->
    </form>
  </div>

  <script src="assets/js/main.js"></script>
</body>

</html>
```

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
.required::after {
  content: '*';
  color: red;
  margin-left: 4px;
}

.error-message {
  color: #ff4444;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

nav {
  padding: 2rem 0;
}

nav ul {
  display: flex;
  list-style: none;
  padding: 0;
  margin: 0;
  position: relative;
  justify-content: space-between;
  align-items: center;
  max-width: 800px;
  margin: 0 auto;
}

nav ul::before {
  position: absolute;
  top: 50%;
  left: 0;
  width: 100%;
  height: 2px;
  background: #e0e0e0;
  z-index: 1;
}

nav ul li {
  position: relative;
  z-index: 2;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

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

nav ul li.active {
  color: #1095c1;
  font-weight: bold;
}

.buttons {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.tipo-cadastro {
  display: flex;
  gap: 2rem;
  justify-content: center;
  margin-bottom: 2rem;
}

.toast-container {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 9999;
}

.toast {
  padding: 1rem 1.5rem;
  margin-bottom: 0.5rem;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  opacity: 0;
  transform: translateX(100%);
  transition: all 0.3s ease-in-out;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Transição de entrada */
.toast.visible {
  opacity: 1;
  transform: translateX(0);
}

/* Transição de saída */
.toast.removing {
  opacity: 0;
  transform: translateX(100%);
}

.toast.success {
  background-color: #48bb78;
  color: white;
}

.toast.error {
  background-color: #f56565;
  color: white;
}

/* Ícone de fechar */
.toast-close {
  margin-left: auto;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.toast-close:hover {
  opacity: 1;
}
```

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
