# N+1 no Django 6.1: o fim do select_related?

Publicado em 20/09/2026.

<a href="https://youtu.be/Tiyg4H519x0">
    <img src="../.gitbook/assets/youtube.png">
</a>

Doc: [https://docs.djangoproject.com/en/6.1/topics/db/fetch-modes/](https://docs.djangoproject.com/en/6.1/topics/db/fetch-modes/)

## O problema

N+1: 1 query para listar os livros e mais N para buscar o autor de cada um.

* Pegue isso no teste com `assertNumQueries`.
* Para enxergar enquanto desenvolve, olhe o SQL gerado: use o Django Debug Toolbar ou configure o logger do banco.

## Fetch modes (Django 6.1)

* Com `FETCH_PEERS`, ao acessar um campo não carregado, o Django busca esse campo para todas as instâncias do mesmo queryset. Vale para FK, one-to-one e reversos.
* Há também um modo que levanta exceção ao acessar um campo não carregado: o N+1 deixa de ser silencioso.

## E o select_related?

Continua valendo: use `select_related("author")` onde o acesso é previsível e passe os relacionamentos explicitamente. Deixe o `FETCH_PEERS` para código genérico, como admin e templates reaproveitados.

## Shorts relacionados

* [Django 6.1 parte 1](https://youtube.com/shorts/VDFvS34mL9A) (15/09/2026)
* [Django 6.1 parte 2](https://youtube.com/shorts/B35bLdqLGqE) (17/09/2026)
* [select_related vs prefetch_related - Junior vs Senior](https://youtube.com/shorts/_VV1Odkk0Wo) (01/10/2026)
