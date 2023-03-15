# Dica 60 - Django: Adicionando atributos extras no formulário

<a href="https://youtu.be/s8U_YBExsQ0">
    <img src="../.gitbook/assets/youtube.png">
</a>

Repo: [https://gitlab.com/rg3915/exame-inline](https://gitlab.com/rg3915/exame-inline)

Veja como adicionar atributos extras no formulário.

```python
class CareItemsForm(forms.ModelForm):
    id = forms.IntegerField()

    class Meta:
        model = CareItems
        fields = ('care', 'id', 'exam', 'is_done')

    def __init__(self, *args, **kwargs):
        super(CareItemsForm, self).__init__(*args, **kwargs)

        ...

        pk = reverse('exam:care_update_exam', kwargs={'pk': self.instance.pk})
        self.fields['is_done'].widget.attrs['hx-get'] = f'{pk}'
        self.fields['is_done'].widget.attrs['hx-swap'] = f'none'

```