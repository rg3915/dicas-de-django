from django.core.mail import send_mail
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods

from .forms import ContactForm


@require_http_methods(['POST'])
def send_contact(request):
    form = ContactForm(request.POST or None)

    if form.is_valid():
        subject = form.cleaned_data.get('title')
        message = form.cleaned_data.get('body')
        sender = form.cleaned_data.get('email')
        send_mail(
            subject,
            message,
            sender,
            ['localhost'],
            fail_silently=False,
        )
        return redirect('core:index')
