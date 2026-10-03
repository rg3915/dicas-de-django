# Django + InertiaJS (Vue) - palestra

Publicado em 09/09/2026.

<a href="https://youtu.be/b3GmwJQWLrs">
    <img src="../.gitbook/assets/youtube.png">
</a>

Palestra apresentada no DevConverge LATAM em 05/09/2026: Django e VueJS com InertiaJS.

## Pontos principais

* A view do Django usa o `render` do Inertia e manda os dados como props direto para o componente Vue. Sem API REST, sem DRF, sem CORS.
* As rotas ficam só no Django: o Vue tem apenas componentes, sem Vue Router. A autenticação é a do Django, sem token no navegador.
* Inertia é para monolito, consumo próprio. Se a sua API tem outros consumidores (app mobile, terceiros), aí sim vale uma API REST.
