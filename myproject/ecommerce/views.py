import uuid

from django.shortcuts import redirect, render

from myproject.product.models import Product

from .models import Order, OrderItems


def order_create(request):
    template_name = 'ecommerce/order_form.html'
    products = Product.objects.all()

    if request.method == 'POST':
        data = request.POST
        nf = data.get('nf')
        _products = data.getlist('product')
        prices = data.getlist('price')
        quantitys = data.getlist('quantity')

        # Pega as instancias de Product.
        products = [Product.objects.get(pk=pk) for pk in _products]

        # Junta as 3 listas
        items = zip(products, prices, quantitys)

        # Cria a ordem de compra
        order = Order.objects.create(nf=nf)

        aux_list = []
        for item in tuple(items):
            obj = OrderItems(
                order=order,
                product=item[0],
                price=item[1],
                quantity=item[2],
            )
            aux_list.append(obj)

        OrderItems.objects.bulk_create(aux_list)
        return redirect('ecommerce:order_result', pk=order.pk)

    context = {'products': products}
    return render(request, template_name, context)


def add_row(request):
    template_name = 'ecommerce/row_result.html'
    products = Product.objects.all()

    code = uuid.uuid4().hex[:7]

    context = {'products': products, 'code': code}
    return render(request, template_name, context)


def product_price(request):
    template_name = 'ecommerce/product_price.html'
    pk = request.GET.get('product')
    code = request.GET.get('code', '')  # importante por causa do 1º id_price.

    product = Product.objects.get(pk=pk)

    context = {'price': product.price, 'code': code}
    return render(request, template_name, context)


def order_result(request, pk):
    template_name = 'ecommerce/order_result.html'
    order = Order.objects.get(pk=pk)
    context = {'object': order}
    return render(request, template_name, context)
