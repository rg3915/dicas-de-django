# 1 - Django boilerplate e cookiecutter-django

 [![](https://github.com/rg3915/dicas-de-django/tree/f9544195375eae8e191df5b231bc72f93e99e582/img/youtube.png)](https://youtu.be/OYcOpcPcp8Y)

[boilerplatesimple.sh](https://gist.github.com/rg3915/b363f5c4a998f42901705b23ccf4b8e8)

[boilerplate2.sh](https://gist.github.com/rg3915/a264d0ade860d2f2b4bf)

[cookiecutter-django](https://github.com/pydanny/cookiecutter-django)

```text
python -m venv .venv
source .venv/bin/activate

pip install "cookiecutter>=1.7.0"
cookiecutter https://github.com/pydanny/cookiecutter-django
pip install -r requirements/local.txt 
python manage.py migrate

createdb myproject -U postgres

python manage.py migrate
```

