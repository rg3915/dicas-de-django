from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductForm
from .models import Product


def product_list(request):
    template_name = 'product/product_list.html'
    object_list = Product.objects.all()
    context = {'object_list': object_list}
    return render(request, template_name, context)


def product_detail(request, pk):
    template_name = 'product/product_detail.html'
    instance = get_object_or_404(Product, pk=pk)

    context = {'object': instance}
    return render(request, template_name, context)


def product_create(request):
    template_name = 'product/product_form.html'
    form = ProductForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('product:product_list')

    context = {'form': form}
    return render(request, template_name, context)


def product_update(request, pk):
    template_name = 'product/product_form.html'
    instance = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=instance)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('product:product_list')

    context = {'form': form, 'object': instance}
    return render(request, template_name, context)


def product_delete(request, pk):
    instance = get_object_or_404(Product, pk=pk)
    instance.delete()
    return redirect('product:product_list')
