# crm/admin.py
from django.contrib import admin

from .models import PF, PJ, Customer, Pessoa, Seller


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'email', 'linkedin')
    search_fields = ('first_name', 'last_name', 'email')


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'email', 'internal', 'commission')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('internal',)


@admin.register(Pessoa)
class PessoaAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'email')
    search_fields = ('first_name', 'last_name', 'email')


@admin.register(PF)
class PFAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'email', 'cpf', 'rg')
    search_fields = ('first_name', 'last_name', 'email')


@admin.register(PJ)
class PJAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'email', 'cnpj', 'ie')
    search_fields = ('first_name', 'last_name', 'email')
