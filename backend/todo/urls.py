from django.urls import include, path

from backend.todo import views as v

app_name = 'todo'

todo_patterns = [
    path('', v.todos, name='todos'),  # noqa E501
    path('<int:pk>/done/', v.todo_done, name='todo_done'),  # noqa E501
    path('<int:pk>/delete/', v.todo_delete, name='todo_delete'),  # noqa E501
]

urlpatterns = [
    path('', v.todo_list, name='todo_list'),  # noqa E501
    path('api/v1/', include(todo_patterns)),
]
