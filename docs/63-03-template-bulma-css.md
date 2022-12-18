# Dica 03 - Criando um template com Bulma CSS

VIDEO EM BREVE.

```
mkdir -p src/pages/bulma
touch src/pages/bulma/index.html

python -m http.server 8000
```

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
  <link rel="shortcut icon" href="https://bulma.io/favicons/favicon-32x32.png?v=201701041855">
  <title>Bulma CSS</title>

  <!-- Bulma -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css">
</head>
<body>
  <div class="container">
    <div class="notification is-primary">
      <p>Esta página está usando <a href="https://bulma.io/">Bulma CSS</a>.</p>
    </div>

    <div class="columns">
      <div class="column">
        <!-- card -->
        <!-- https://bulma.io/documentation/components/card/ -->
      </div>

      <div class="column">
        <!-- form -->
        <!-- https://bulma.io/documentation/form/general/#complete-form-example -->
      </div>
    </div>

    <!-- buttons -->
    <!-- https://bulma.io/documentation/elements/button/#colors -->
  </div>
</body>
</html>
```

## Links

[https://bulma.io/](https://bulma.io/)

[https://bulma.io/documentation/components/card/](https://bulma.io/documentation/components/card/)

[https://bulma.io/documentation/form/general/#complete-form-example](https://bulma.io/documentation/form/general/#complete-form-example)

[https://bulma.io/documentation/elements/button/#colors](https://bulma.io/documentation/elements/button/#colors)