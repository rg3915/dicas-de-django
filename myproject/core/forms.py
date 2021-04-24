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
