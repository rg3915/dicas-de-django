# 35 - Django: passando usuário logado no formulário

<a href="https://youtu.be/69jPO_v6ldI">
    <img src="../.gitbook/assets/youtube.png">
</a>


```python
# forms.py
from django import forms

from .models import Person


class PersonForm(forms.ModelForm):

    class Meta:
        model = Person
        fields = '__all__'

    def __init__(self, user=None, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        # my_field = MyModel.objects.filter(user=user)
        if user.is_authenticated:
            print(user)
        else:
            print('Não')
```


```python
# views.py
def person_create(request):
    template_name = 'core/person_form.html'
    # Não esquecer do request.user como primeiro parâmetro.
    form = PersonForm(request.user, request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('person:person_list')

    context = {'form': form}
    return render(request, template_name, context)
```

```python
# models.py
class Person(UuidModel):
    first_name = models.CharField('nome', max_length=50)
    last_name = models.CharField('sobrenome', max_length=50, null=True, blank=True)  # noqa E501
    email = models.EmailField(null=True, blank=True)

    class Meta:
        ordering = ('first_name',)
        verbose_name = 'pessoa'
        verbose_name_plural = 'pessoas'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name or ""}'.strip()

    def __str__(self):
        return self.full_name
```
