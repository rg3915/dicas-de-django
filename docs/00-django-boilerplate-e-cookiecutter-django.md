# 1 - Django boilerplate e cookiecutter-django

<a href="https://youtu.be/OYcOpcPcp8Y">
    <img src="../.gitbook/assets/youtube.png">
</a>

[django-boilerplate](https://github.com/rg3915/django-boilerplate)

[boilerplate2.sh](https://gist.github.com/rg3915/a264d0ade860d2f2b4bf)

[cookiecutter-django](https://github.com/pydanny/cookiecutter-django)

```
python -m venv .venv
source .venv/bin/activate

pip install "cookiecutter>=1.7.0"
cookiecutter https://github.com/pydanny/cookiecutter-django
pip install -r requirements/local.txt 
python manage.py migrate

createdb myproject -U postgres

python manage.py migrate
```
