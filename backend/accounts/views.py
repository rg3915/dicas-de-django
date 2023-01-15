# accounts/views.py
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import (
    LoginView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView
)
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render

from backend.accounts.services import send_mail_to_user

from .forms import CustomUserForm, MyAuthenticationForm
from .models import AuditEntry, User
from .signals import user_login_password_failed


def signup(request):
    '''
    Cadastra Usuário.
    '''
    template_name = 'registration/registration_form.html'
    form = CustomUserForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            send_mail_to_user(request=request, user=user)
            return redirect('login')

    return render(request, template_name)


class MyPasswordResetConfirm(PasswordResetConfirmView):
    '''
    Requer password_reset_confirm.html
    '''

    def form_valid(self, form):
        self.user.is_active = True
        self.user.save()
        return super(MyPasswordResetConfirm, self).form_valid(form)


class MyPasswordResetComplete(PasswordResetCompleteView):
    '''
    Requer password_reset_complete.html
    '''
    ...


class MyPasswordReset(PasswordResetView):
    '''
    Requer
    registration/password_reset_form.html
    registration/password_reset_email.html
    registration/password_reset_subject.txt  Opcional
    '''
    ...


class MyPasswordResetDone(PasswordResetDoneView):
    '''
    Requer
    registration/password_reset_done.html
    '''
    ...


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


class MyLoginView(LoginView):
    template_name = 'registration/login.html'
    form_class = MyAuthenticationForm

    def form_invalid(self, form):
        email = form.data.get('username')

        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                pass
            else:
                # Dispara o signal quando o usuário existe, mas a senha está errada.
                user_login_password_failed.send(
                    sender=__name__,
                    request=self.request,
                    user=user
                )

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        user = form.get_user()

        # Autentica usuário
        auth_login(self.request, user)

        # Zera o AuditEntry
        AuditEntry.objects.filter(
            email=user.email,
            action='user_login_password_failed'
        ).delete()

        return HttpResponseRedirect(self.get_success_url())
