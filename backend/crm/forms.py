from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(max_length=255)
    email = forms.EmailField()  # sender
    title = forms.CharField(max_length=100)  # subject
    body = forms.CharField(widget=forms.Textarea)  # message
