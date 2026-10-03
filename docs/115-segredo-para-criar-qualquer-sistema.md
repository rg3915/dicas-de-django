# O segredo para criar qualquer sistema em Django

Publicado em 12/03/2026.

<a href="https://youtu.be/ouw9bCYAvxA">
    <img src="../.gitbook/assets/youtube.png">
</a>

Github: [https://github.com/rg3915/django-modelagem](https://github.com/rg3915/django-modelagem)

Pedido, compra, orçamento, venda, ordem de serviço, estoque (saída), carrinho de compras: todos têm algo em comum, **cliente + itens + produtos + quantidade + preço**. Modele uma vez e reaproveite.

O vídeo mostra a modelagem com **Mermaid**, o **SQL** e os **Django Models**, além de um carrinho de compras em JavaScript puro com **PicoCSS**.

## Dicas de modelagem

* A base: um model `Pedido` com FK para `Cliente`, status e data, e um `PedidoItem` com FK para o pedido e o produto, quantidade e preço.
* Crie um `BaseModel` abstrato no app `core` (id UUID, criado em, modificado em, ativo) e herde em todos os models.
* Use `TextChoices` para o status do pedido.
* Defina `get_absolute_url` no model e a `CreateView` redireciona sozinha para o detalhe depois de salvar.
* Siga os nomes padrão das CBVs (`cliente_list.html`, `cliente_form.html`, `object_list`) e dispense `template_name` e `context_object_name`.
* No admin, use `TabularInline` para editar os itens na mesma tela do pedido.
