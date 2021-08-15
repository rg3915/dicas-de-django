from django.conf import settings
from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import path
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter

from .models import Article, Category, Person

# from .forms import ArticleAdminForm


admin.site.login_template = 'myproject/core/templates/admin/login.html'


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'get_published_date',
        'get_category',
        'status'
    )
    search_fields = ('title',)
    list_filter = (
        ('published_date', DateRangeFilter),
        ('modified', DateTimeRangeFilter),
        'category',
        'status',
    )
    # readonly_fields = ('slug',)
    date_hierarchy = 'published_date'
    # form = ArticleAdminForm
    list_editable = ('title', 'status')
    actions = ('make_published',)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
            obj.save()
        super(ArticleAdmin, self).save_model(request, obj, form, change)

    def make_published(self, request, queryset):
        count = queryset.update(status='p')

        if count == 1:
            msg = '{} artigo foi publicado.'
        else:
            msg = '{} artigos foram publicados.'

        self.message_user(request, msg.format(count))

    make_published.short_description = "Publicar artigos"

    def get_published_date(self, obj):
        if obj.published_date:
            return obj.published_date.strftime('%d/%m/%Y')

    get_published_date.short_description = 'Data de Publicação'

    def get_category(self, obj):
        if obj.category:
            return obj.category.title

    get_category.short_description = 'Categoria'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                'botao-artigo/',
                self.admin_site.admin_view(self.minha_funcao, cacheable=True)
            ),
        ]
        return my_urls + urls

    def minha_funcao(self, request):
        print('Ao clicar no botão, faz alguma coisa...')
        messages.add_message(
            request,
            messages.INFO,
            'Ação realizada com sucesso.'
        )
        return redirect('admin:core_article_changelist')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    actions = None

    def has_add_permission(self, request, obj=None):
        return False

    if not settings.DEBUG:
        def has_delete_permission(self, request, obj=None):
            return False

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                'botao-da-app/',
                self.admin_site.admin_view(
                    self.minha_funcao_category, cacheable=True)
            ),
        ]
        return my_urls + urls

    def minha_funcao_category(self, request):
        print('Ao clicar no botão, faz alguma coisa em category...')
        messages.add_message(
            request,
            messages.INFO,
            'Ação realizada com sucesso.'
        )
        return redirect('admin:core_category_changelist')


admin.site.register(Person)
