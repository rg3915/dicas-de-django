# Dica 20 - Templates

VIDEO EM BREVE.

O básico sobre templates é:

## Subpasta no templates com o mesmo nome da app

Definir uma subpasta no templates com o mesmo nome da app.

```
mkdir -p accounts/templates/accounts
```

## Templates

### Lista de itens

```
touch accounts/templates/accounts/user_list.html
```

### Detalhes de um item

```
touch accounts/templates/accounts/user_detail.html
```

### Template de Formulário

```
touch accounts/templates/accounts/user_form.html
```

## Conteúdo de cada template

### user_list.html

```html
{% extends "base.html" %}

{% block content %}
  <table>
    <thead>
      <tr>
        <th>Título</th>
      </tr>
    </thead>
    <tbody>
      {% for object in object_list %}
        <tr>
          <td>{{ object }}</td>
        </tr>
      {% endfor %}
    </tbody>
  </table>
{% endblock content %}
```

### user_detail.html

```html
{% extends "base.html" %}

{% block content %}
  <div>
    <div>
      <h1>Detalhes: {{ object }}</h1>
    </div>
    <div>
      <a href="javascript: history.go(-1)">Voltar</a>
    </div>

    <div>
      <img src="https://via.placeholder.com/500" alt="">
    </div>

    <!-- Título -->
    <div>
      <div>
        <div>Título</div>
        <div>{{ object.title }}</div>
      </div>
    </div>

    <!-- Descrição -->
    <div>
      <div>
        <div>Descrição</div>
        <div>{{ object.description }}</div>
      </div>
    </div>

  </div>
{% endblock content %}
```

### user_form.html

```html
{% extends "base.html" %}
{% load widget_tweaks %}

{% block content %}
  <div>
    <div>
      <div>
        <h2>
          {% if object.pk %}
            Editar
          {% else %}
            Adicionar
          {% endif %}
          Usuário
        </h2>

        {% if form.errors %}
          {% for error in form.non_field_errors %}
            <p class="text-red-500">{{ error }}</p>
          {% endfor %}
        {% endif %}

        <form action="." method="POST" enctype="multipart/form-data">
          {% csrf_token %}

          {% for field in form.visible_fields %}
            <div>
              <label>{{ field.label }}</label>
              {% render_field field class="" %}
            </div>
            <span>{{ field.help_text }}</span>

            {% for error in field.errors %}
              <span class="text-red-500">{{ error }}</span> <br>
            {% endfor %}
          {% endfor %}

          <div class="flex flex-col sm:flex-row">
            <button type="submit">Salvar</button>
            <a href="">
              Cancelar
            </a>
          </div>
        </form>
      </div>
    </div>
  </div>
{% endblock content %}
```

## urls.py

```python
# accounts/urls.py
from django.contrib.auth.views import LogoutView
from django.urls import include, path

from backend.accounts import views as v

# A ordem das urls é importante por causa do slug, quando existir.
user_patterns = [
    path('', v.user_list, name='user_list'),  # noqa E501
    path('create/', v.user_create, name='user_create'),  # noqa E501
    path('<int:pk>/', v.user_detail, name='user_detail'),  # noqa E501
    path('<int:pk>/update/', v.user_update, name='user_update'),  # noqa E501
]

urlpatterns = [
    path('login/', v.MyLoginView.as_view(), name='login'),  # noqa E501
    path('logout/', LogoutView.as_view(), name='logout'),  # noqa E501
    ...

    path('users/', include(user_patterns)),
]
```

## views.py

```python
def user_list(request):
    template_name = 'accounts/user_list.html'
    object_list = User.objects.exclude(email='admin@email.com')
    context = {'object_list': object_list}
    return render(request, template_name, context)


def user_detail(request, pk):
    template_name = 'accounts/user_detail.html'
    instance = get_object_or_404(User, pk=pk)

    context = {'object': instance}
    return render(request, template_name, context)


def user_create(request):
    template_name = 'accounts/user_form.html'
    form = CustomUserForm(request.POST or None)

    context = {'form': form}
    return render(request, template_name, context)


def user_update(request, pk):
    template_name = 'accounts/user_form.html'
    instance = get_object_or_404(User, pk=pk)
    form = CustomUserForm(request.POST or None, instance=instance)

    context = {
        'object': instance,
        'form': form,
    }
    return render(request, template_name, context)
```

## forms.py

```python
class CustomUserForm(forms.ModelForm):
    first_name = forms.CharField(
        label='Nome',
        max_length=150,
    )
    last_name = forms.CharField(
        label='Sobrenome',
        max_length=150,
    )
    email = forms.EmailField(
        label='E-mail',
    )

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
        )
```