# Atualizando um projeto para o Django 6.0

Publicado em 02/03/2026.

<a href="https://youtu.be/R1IiagAoZio">
    <img src="../.gitbook/assets/youtube.png">
</a>

Projeto: [https://github.com/rg3915/django-experience](https://github.com/rg3915/django-experience)

## Passo a passo

1. Comece pelo `requirements.txt`: atualize os pacotes, rode `pip freeze` e regrave o arquivo com as versões novas.
2. Siga o README e corrija o que estiver faltando nele (por exemplo, subir o Postgres com `docker compose` antes do `migrate`).
3. Atualize junto o Django REST Framework e registre no README as versões novas de Python, Django e DRF.
4. Rode `migrate`, `runserver` e navegue pelas telas e pela API. Erro de upgrade aparece no uso, não no `pip install`.
