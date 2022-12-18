# 2 - Usando http.server

Crie um `public/index.html`.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
  <link rel="shortcut icon" href="http://getskeleton.com/dist/images/favicon.png">
  <title>Skeleton CSS</title>

  <!-- Skeleton -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css">
</head>
<body>
  <h1>Skeleton template example</h1>
  <p>Esta página está usando <a href="http://getskeleton.com/">skeleton CSS</a>.</p>
  <button class="button-primary">Botão</button>
</body>
</html>
```

E simplesmente digite

```
python -m http.server 8000
```

## Links

http://getskeleton.com/

https://cdnjs.com/libraries/skeleton

