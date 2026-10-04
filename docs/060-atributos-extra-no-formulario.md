# Dica 60 - Django: Adicionando atributos extras no formulário

**Versões usadas no vídeo:** Django 4.0, Python 3.9, Bootstrap 4.4.1 e htmx 1.6.1.
{: .versoes }

<a href="https://youtu.be/s8U_YBExsQ0">
    <img src="../.gitbook/assets/youtube.png">
</a>

Repo: [https://gitlab.com/rg3915/exame-inline](https://gitlab.com/rg3915/exame-inline)

Veja como adicionar atributos extras no formulário.

Neste tutorial vamos colocar atributos HTML que o Django não conhece (no caso, os atributos `hx-get` e `hx-swap` do [htmx](https://htmx.org/)) num campo de formulário, direto no `forms.py`, em vez de tentar montá-los no template.

O exemplo vem do projeto **exame-inline**: um atendimento médico (`Care`) tem vários itens de exame (`CareItems`), editados com um `inlineformset_factory`. Cada item tem um checkbox **Feito?** (`is_done`). A ideia é que, ao clicar no checkbox, o htmx chame uma URL que grava o `is_done` daquele item na hora, sem enviar o formulário inteiro.

## O problema: chave dentro de chave

A URL que o checkbox tem que chamar depende do `pk` de cada item, por exemplo `/exam/9/update/exam/`. A primeira tentativa foi montar o atributo no template, algo como:

```html
{% render_field field {{form.id.value}} %}
```

Isso não funciona: no template do Django não dá para colocar uma variável `{{ ... }}` dentro de uma tag `{% ... %}`. A alternativa no template seria uma gambiarra, escrevendo o `<input>` na mão e mantendo a numeração do formset (`items-0-is_done`, `items-1-is_done`, ...) sincronizada com o `forloop.counter0`.

A forma correta é definir os atributos adicionais no próprio formulário, no `__init__`, onde temos acesso a `self.instance.pk` e podemos usar o `reverse` para montar a URL.

## Pré-requisitos

O projeto usado no vídeo pode ser clonado do GitLab:

```bash
git clone https://gitlab.com/rg3915/exame-inline.git
cd exame-inline
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python contrib/env_gen.py
python manage.py migrate
python manage.py createsuperuser --username="admin" --email=""
```

O `requirements.txt` da época:

```
django-extensions==3.1.5
Django==4.0
python-decouple==3.5
```

O htmx é carregado no fim do `base.html`, junto com o JavaScript do Bootstrap:

```html
<!-- backend/core/templates/base.html (trecho) -->
  <script src="https://code.jquery.com/jquery-3.4.1.min.js"></script>
  <!-- Bootstrap core JS -->
  <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js"></script>
  <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js"></script>
  <script src="https://unpkg.com/htmx.org@1.6.1"></script>
</body>
```

## Os models

```python
# backend/exam/models.py
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse_lazy


class Patient(models.Model):
    registration = models.CharField('matrícula', max_length=7, unique=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='paciente',
        related_name='patients'
    )

    class Meta:
        ordering = ('user__first_name',)
        verbose_name = 'paciente'
        verbose_name_plural = 'pacientes'

    def __str__(self):
        return f'{self.user.first_name}'


class Exam(models.Model):
    title = models.CharField('título', max_length=50, unique=True)

    class Meta:
        ordering = ('title',)
        verbose_name = 'exame'
        verbose_name_plural = 'exames'

    def __str__(self):
        return f'{self.title}'


class Care(models.Model):
    doctor = models.CharField('médico', max_length=100)
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        verbose_name='paciente',
        related_name='cares',
    )
    created = models.DateTimeField('data', auto_now_add=True)

    class Meta:
        ordering = ('doctor',)
        verbose_name = 'atendimento'
        verbose_name_plural = 'atendimentos'

    def __str__(self):
        return f'{self.doctor}'

    def get_absolute_url(self):
        return reverse_lazy('exam:care_detail', kwargs={'pk': self.pk})


class CareItems(models.Model):
    care = models.ForeignKey(
        Care,
        on_delete=models.CASCADE,
        verbose_name='atendimento',
        related_name='care_items',
    )
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        verbose_name='exame',
        related_name='care_items_exam',
    )
    is_done = models.BooleanField('feito?', default=False)

    class Meta:
        ordering = ('pk',)
        verbose_name = 'atendimento item'
        verbose_name_plural = 'atendimento itens'

    def __str__(self):
        return f'{self.pk}'
```

## A URL que o checkbox vai chamar

O nome da URL é `care_update_exam`, no namespace `exam`. É esse nome que o `reverse` vai traduzir.

```python
# backend/exam/urls.py
from django.urls import path

from backend.exam import views as v

app_name = 'exam'

urlpatterns = [
    path('', v.care_list, name='care_list'),
    path('create/', v.care_create, name='care_create'),
    path('<int:pk>/', v.care_detail, name='care_detail'),
    path('<int:pk>/update/', v.care_update, name='care_update'),
    path('<int:pk>/update/exam/', v.care_update_exam, name='care_update_exam'),
]
```

No `backend/urls.py`, o app é incluído com `path('exam/', include('backend.exam.urls', namespace='exam'))`.

## A view que grava o `is_done`

Quando o checkbox está marcado, o htmx envia o valor do campo na query string (`?items-0-is_done=on`). Quando está desmarcado, não envia nada. A view só verifica se veio algum valor:

```python
# backend/exam/views.py (trecho)
from django.http import HttpResponse

from .models import CareItems


def care_update_exam(request, pk):
    '''
    Atualiza cada exame marcando is_done como True ou False.
    '''
    care_items = CareItems.objects.get(pk=pk)
    # Verifica se a lista com os valores do request tem alguma coisa ou
    # se a lista vem vazia.
    is_done_list = list(request.GET.values())

    if is_done_list:
        is_done = True
    else:
        is_done = False

    care_items.is_done = is_done
    care_items.save()
    return HttpResponse(pk)
```

A view de edição do atendimento monta o formulário principal e o formset:

```python
# backend/exam/views.py (trecho)
def care_update(request, pk):
    template_name = 'exam/care_update.html'
    care_instance = Care.objects.get(pk=pk)

    form = CareForm(request.POST or None, instance=care_instance, prefix='main')
    formset = CareItemsFormset(request.POST or None, instance=care_instance, prefix='items')

    context = {'form': form, 'formset': formset}
    return render(request, template_name, context)
```

## Os atributos extras no `forms.py`

Aqui está a dica. No `__init__` do `CareItemsForm`, depois de chamar o `super()`:

1. `self.instance.pk` é o `pk` do item do formset que está sendo montado.
2. `reverse('exam:care_update_exam', kwargs={'pk': ...})` traduz o nome da URL para o caminho, por exemplo `/exam/9/update/exam/`.
3. `widget.attrs` é um dicionário com os atributos HTML do campo. Tudo o que você colocar nele sai no `<input>`, inclusive atributos que o Django não conhece, como `hx-get` e `hx-swap`.

```python
# backend/exam/forms.py
from django import forms
from django.forms import inlineformset_factory
from django.urls import reverse

from .models import Care, CareItems


class CareForm(forms.ModelForm):
    id = forms.IntegerField(required=False)

    class Meta:
        model = Care
        fields = ('id', 'doctor', 'patient')

    def __init__(self, *args, **kwargs):
        super(CareForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        self.fields['id'].label = ''
        self.fields['id'].widget = forms.HiddenInput()


class CareItemsForm(forms.ModelForm):
    id = forms.IntegerField()

    class Meta:
        model = CareItems
        fields = ('care', 'id', 'exam', 'is_done')

    def __init__(self, *args, **kwargs):
        super(CareItemsForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        self.fields['care'].label = ''
        self.fields['care'].widget = forms.HiddenInput()

        self.fields['id'].label = ''
        self.fields['id'].widget = forms.HiddenInput()

        pk = reverse('exam:care_update_exam', kwargs={'pk': self.instance.pk})
        self.fields['is_done'].widget.attrs['hx-get'] = f'{pk}'
        self.fields['is_done'].widget.attrs['hx-swap'] = f'none'


CareItemsFormset = inlineformset_factory(
    Care,
    CareItems,
    form=CareItemsForm,
    extra=0,
    can_delete=False,
    min_num=1,
    validate_min=True,
)
```

Apesar do nome, a variável `pk` guarda a URL já traduzida, e não o número. O `hx-swap="none"` diz ao htmx para não trocar nada na página com a resposta: só queremos gravar o valor no banco.

## O template

Como os atributos já estão no widget, o template só renderiza o campo, sem nenhuma tag dentro de outra:

```html
<!-- backend/exam/templates/exam/care_update.html -->
{% extends "base.html" %}
{% load static %}

{% block css %}

<style>
  .form-control {
    margin: 10px;
  }
</style>

{% endblock css %}

{% block content %}

<h1>Editar atendimento</h1>

<div class="row">
  <div class="cols">
    <form method="POST" novalidate>
      {% csrf_token %}

      {{ form.as_p }}

      {{ formset.management_form }}

      <div class="row">
        <div class="cols">

          <legend>Itens</legend>

          {% for care_item_form in formset %}
            <div id="care" class="form-inline">
              <div id="item-{{ forloop.counter0 }}" class="form-group">
                {{ care_item_form.care }}
                {{ care_item_form.id }}

                {{ care_item_form.exam.label }}
                {{ care_item_form.exam }}

                {{ care_item_form.is_done.label }}
                {{ care_item_form.is_done }}  <!-- Os atributos hx-get, hx-swap estão definidos no forms.py -->
              </div>
            </div>
          {% endfor %}

        </div>
      </div>

    </form>

    <a href="{% url 'exam:care_detail' form.id.value %}" class="btn btn-primary">Fechar</a>
  </div>
</div>

{% endblock content %}
```

## Resultado

Abra `http://localhost:8000/exam/9/update/` (troque o 9 pelo id do seu atendimento) e inspecione um checkbox no DevTools. O HTML gerado é parecido com este:

```html
<input type="checkbox" name="items-0-is_done" class="form-control" hx-get="/exam/1/update/exam/" hx-swap="none" id="id_items-0-is_done">
```

Cada item do formset recebe a URL com o seu próprio `pk`. Ao marcar ou desmarcar o checkbox, o htmx faz um `GET` nessa URL e a view grava `is_done` como `True` ou `False`. Ao voltar para a página de detalhes do atendimento (`/exam/9/`), os exames aparecem com ✔ ou ✖ conforme o que foi marcado.

## Conclusão

Sempre que precisar de um atributo HTML que dependa de dados do objeto (uma URL com `pk`, um `data-*`, um atributo do htmx), defina-o no `__init__` do formulário com `self.fields['campo'].widget.attrs['atributo'] = valor`. Assim o template fica limpo e você evita o problema de chave dentro de chave.
