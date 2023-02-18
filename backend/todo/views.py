import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Todo


def todo_list(request):
    '''
    Renderiza um template para as tarefas.
    '''
    template_name = 'todo/todo_list.html'
    return render(request, template_name)


def todos(request):
    '''
    Retorna as tarefas via API REST, ou adiciona uma nova.
    '''
    todos = Todo.objects.all()

    if request.method == 'POST':
        # Desserializa os dados.
        data = json.loads(request.body)

        # Salva a tarefa.
        todo = Todo.objects.create(task=data['task'])

        # Retorna o objeto.
        return JsonResponse(todo.to_dict())

    data = [todo.to_dict() for todo in todos]
    # Retorna uma lista.
    return JsonResponse(data, safe=False)


@csrf_exempt
@require_http_methods(['POST'])
def todo_done(request, pk):
    '''
    Conclui uma tarefa via API REST.
    '''
    data = json.loads(request.body)
    done = data.get('done')
    try:
        todo = Todo.objects.get(pk=pk)
        todo.done = done
        todo.save()
        return JsonResponse({'success': True})
    except Todo.DoesNotExist:
        return JsonResponse({'success': False})


@csrf_exempt
@require_http_methods(['DELETE'])
def todo_delete(request, pk):
    '''
    Deleta uma tarefa via API REST.
    '''
    todo = Todo.objects.get(pk=pk)
    todo.delete()
    return JsonResponse({'success': True})
