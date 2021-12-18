# Dica 55 - Rodando Django em https localmente com runserver_plus

<a href="https://youtu.be/4nI3lcUAeC4">
    <img src="../.gitbook/assets/youtube.png">
</a>

Github: [https://github.com/rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django)

```
pip install Werkzeug
```

```
python manage.py runserver_plus --print-sql
```

## HTTPS

```
pip install pyOpenSSL
python manage.py runserver_plus --cert-file /tmp/cert.crt
```

Entre em https://localhost:8000

