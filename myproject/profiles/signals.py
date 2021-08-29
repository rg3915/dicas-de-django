from .models import Profile


def user_pre_save_receiver(sender, instance, *args, **kwargs):
    print(instance.username, instance.id)  # None
    # trigger pre_save
    # NÃO FAÇA ISSO -> instance.save()
    # trigger post_save


def update_user_profile(sender, instance, created, **kwargs):
    if created:
        print('Usuário criado', instance.id, instance.username)
        Profile.objects.create(user=instance)
    instance.profile.save()
