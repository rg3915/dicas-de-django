from django.apps import AppConfig


class ProductConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.product'

    def ready(self):
        from django.db.models.signals import pre_save

        from .models import Product
        from .signals import product_pre_save

        pre_save.connect(product_pre_save, sender=Product)
