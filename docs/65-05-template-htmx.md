# Dica 05 - htmx simples


VIDEO EM BREVE.

```
mkdir -p src/pages/htmx
touch src/pages/htmx/index.html
touch src/pages/htmx/component.html

python -m http.server 8000
```

```html
<!-- index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
  <link rel="shortcut icon" href="https://tailwindcss.com/favicons/favicon-32x32.png?v=3">
  <title>htmx</title>

  <!-- TailwindCSS -->
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
  <div class="flex flex-col sm:w-1/2">
    <div class="overflow-x-auto sm:-mx-6 lg:-mx-8">
      <div class="py-2 inline-block min-w-full sm:px-6 lg:px-8">
        <div class="overflow-hidden">
          <table class="min-w-full">
            <thead class="border-b">
              <tr>
                <th scope="col" class="text-sm font-medium text-gray-900 px-6 py-4 text-left">
                  Nome
                </th>
              </tr>
            </thead>
            <tbody id="tbody">
              <tr class="border-b">
                <td class="text-sm text-gray-900 font-light px-6 py-4 whitespace-nowrap">
                  <div class="mb-3 xl:w-96">
                    <input
                      type="text"
                      class="
                        form-control
                        block
                        w-full
                        px-3
                        py-1.5
                        text-base
                        font-normal
                        text-gray-700
                        bg-white bg-clip-padding
                        border border-solid border-gray-300
                        rounded
                        transition
                        ease-in-out
                        m-0
                        focus:text-gray-700
                        focus:bg-white
                        focus:border-blue-600
                        focus:outline-none
                      "/>
                  </div>
                </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="flex space-x-2 justify-center">
      <button
        type="button"
        class="
          inline-block
          px-6
          py-2.5
          bg-blue-600
          text-white
          font-medium
          text-xs
          leading-tight
          uppercase
          rounded
          shadow-md
          hover:bg-blue-700
          hover:shadow-lg
          focus:bg-blue-700
          focus:shadow-lg
          focus:outline-none
          focus:ring-0
          active:bg-blue-800
          active:shadow-lg
          transition
          duration-150
          ease-in-out
        "
      >
        Adicionar
      </button>
    </div>
  </div>

</body>
</html>```

```html
<!-- index.html -->
<!-- Segunda parte -->

  <!-- htmx -->
  <script src="https://unpkg.com/htmx.org@1.8.4"></script>

    <button
      hx-get="/src/pages/htmx/component.html"
      hx-target="#tbody"
      hx-swap="beforeend"
    >
      Adicionar
    </button>
```

```html
<!-- component.html -->
<tr class="border-b">
  <td class="text-sm text-gray-900 font-light px-6 py-4 whitespace-nowrap">
    <div class="mb-3 xl:w-96">
      <input
        type="text"
        class="
          form-control
          block
          w-full
          px-3
          py-1.5
          text-base
          font-normal
          text-gray-700
          bg-white bg-clip-padding
          border border-solid border-gray-300
          rounded
          transition
          ease-in-out
          m-0
          focus:text-gray-700
          focus:bg-white
          focus:border-blue-600
          focus:outline-none
        "/>
    </div>
  </td>
</tr>
```

## Links

[https://htmx.org/](https://htmx.org/)
