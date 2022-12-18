# 4 - Criando um template com Tailwind CSS

```
mkdir -p src/pages/tailwind
touch src/pages/tailwind/index.html

python -m http.server 8000
```

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
  <link rel="shortcut icon" href="https://tailwindcss.com/favicons/favicon-32x32.png?v=3">
  <title>TailwindCSS</title>

  <!-- TailwindCSS -->
  <script src="https://cdn.tailwindcss.com"></script>

  <style>
    .main-content {
      height: calc(100vh - 4rem - 4rem);
    }
  </style>
</head>
<body class="flex flex-col min-h-screen">
  <header class="h-16 bg-slate-800 text-gray-100 flex justify-center items-center">
    <h1 class="text-2xl font-bold">TailwindCSS</h1>
  </header>

  <main class="flex-auto">
    <div class="flex main-content">
      <!-- aside -->
      <div class="flex flex-col relative w-1/6 bg-stone-800 border-r border-gray-200">
        <!-- button -->
        <button class="absolute -right-4 top-12 h-8 w-8 bg-slate-800 text-gray-50 rounded-full border border-gray-200 z-10"><</button>
      </div>
      <!-- main -->
      <div class="relative w-5/6 bg-zinc-800">
        <div class="absolute h-10 w-10 bg-yellow-500 flex items-center justify-center">1</div>
        <div class="absolute right-0 h-10 w-10 bg-yellow-500 flex items-center justify-center">2</div>
        <div class="absolute right-0 bottom-0 h-10 w-10 bg-yellow-500 flex items-center justify-center">3</div>
        <div class="absolute bottom-0 h-10 w-10 bg-yellow-500 flex items-center justify-center">4</div>
        <div class="absolute top-1/2 left-1/2 h-10 w-10 bg-red-500 flex items-center justify-center">5</div>
        <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 h-10 w-10 bg-yellow-500 flex items-center justify-center">
        5
        <!-- ball -->
        <span class="absolute -right-1.5 -top-1.5 h-3 w-3 bg-blue-500 rounded-full"></span>
        </div>
      </div>
    </div>
  </main>

  <footer class="h-16 bg-slate-800 text-gray-100 flex justify-between items-center px-4 text-lg">
    <h1>Dicas de Django © 2023</h1>
    <h1>by Regis do Python</h1>
  </footer>

</body>
</html>
```

## Links

https://tailwindcss.com/

https://merakiui.com

https://tailwind-elements.com/

https://www.tailwindtoolbox.com/starter-templates

https://flowbite.com/