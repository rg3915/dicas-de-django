# 42 - Custom context processors

O **Custom context processors** é um recurso que nos fornece objetos globais que podemos usar em qualquer parte da nossa aplicação.

```python
cat << EOF > myproject/travel/context_processors.py
from .models import Travel


def travel_count(request):
    travel = Travel.objects.all()
    context = {'total_travel': travel.count()}
    return context

EOF
```

Edite `settings.py`:

```python
TEMPLATES = [
    {
        ...
        'OPTIONS': {
            'context_processors': [
                ...
                # apps
                'myproject.travel.context_processors.travel_count',
            ],
        },
    },
]
```

E em `nav.html`

```html
<li class="nav-item">
    <a class="nav-link" href="{% url 'travel:travel_list' %}">
        Viagens
        <span class="badge badge-warning">{{ total_travel }}</span>
    </a>
</li>
```

