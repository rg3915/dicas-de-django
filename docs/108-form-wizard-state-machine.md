# Form Wizard com máquina de estados (JS)

Publicado em 23/12/2024.

<a href="https://youtu.be/oqJxdjh6Iyk">
    <img src="../.gitbook/assets/youtube.png">
</a>

Um formulário wizard (em várias etapas) com uma **máquina de estados** para gerenciar o fluxo de etapas de forma previsível e escalável.

Github: [https://github.com/rg3915/form-wizard-state-machine](https://github.com/rg3915/form-wizard-state-machine)

## A ideia

Modele o formulário como uma máquina de estados:

* uma lista de estados (as etapas);
* um `currentState`;
* métodos `nextState` e `prevState` para avançar e voltar.

Assim o fluxo fica previsível e fácil de estender.
