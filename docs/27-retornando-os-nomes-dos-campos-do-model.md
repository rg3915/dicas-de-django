# 27 - Retornando os nomes dos campos do model

<a href="https://youtu.be/lU2J5ZCJiyE">
    <img src="../.gitbook/assets/youtube.png">
</a>


```python
$ python manage.py shell_plus

>>> [field.name for field in User._meta.get_fields()]
['logentry',
 'id',
 'password',
 'last_login',
 'is_superuser',
 'username',
 'first_name',
 'last_name',
 'email',
 'is_staff',
 'is_active',
 'date_joined',
 'groups',
 'user_permissions']

>>> [field.name for field in Article._meta.get_fields()]
['id', 'title', 'subtitle', 'slug', 'category', 'published_date']
```
