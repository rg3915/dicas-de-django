# 3 ferramentas que todo projeto Django devia ter

> 📅 **Vídeo agendado:** será publicado no YouTube em **17/10/2026, às 10:00**. O link abaixo passa a funcionar nessa data.

<a href="https://youtube.com/shorts/JmpU-HeKBc4">
    <img src="../.gitbook/assets/youtube.png">
</a>

1. **Django Debug Toolbar**: mostra as consultas de cada página. No exemplo, a listagem fez 51 consultas; com `select_related`, caiu para 1.
2. **Django Extensions**: dezenas de comandos prontos, como o `show_urls`, que lista todas as rotas do projeto.
3. **django-upgrade**: reescreve o código antigo no padrão novo do Django (`admin.site.register` → `@admin.register`, `request.META` → `request.headers`).

```
uvx django-upgrade --target-version 6.1 livros/*.py
```
