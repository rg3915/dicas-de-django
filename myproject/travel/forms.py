from django import forms

from .models import Travel


class TravelForm(forms.ModelForm):
    required_css_class = 'required'

    date_travel = forms.DateField(
        label='Data',
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'type': 'date',
            }),
        input_formats=('%Y-%m-%d',),
    )
    datetime_travel = forms.DateTimeField(
        label='Data/Hora',
        widget=forms.DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={
                'type': 'datetime-local',
            }),
        input_formats=('%Y-%m-%dT%H:%M',),
    )
    time_travel = forms.TimeField(
        label='Tempo',
        widget=forms.TimeInput(
            format='%H:%M',
            attrs={
                'type': 'time',
            }),
        input_formats=('%H:%M',),
    )

    class Meta:
        model = Travel
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(TravelForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
