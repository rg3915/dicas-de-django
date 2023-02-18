const data = document.currentScript.dataset
const csrftoken = data.csrf

const getTodos = () => ({
  url: '/todo/api/v1/',
  todos: [],
  task: '',
  required: false,

  init() {
    this.getData()
  },

  getData() {
    // Pega os dados no backend com fetch.
    fetch(this.url)
      .then(response => response.json())
      .then(data => this.todos = data)
  },

  saveData() {
    // Verifica se task foi preenchido.
    if (!this.task) {
      this.required = true
      return
    }
    // Salva os dados no backend.
    fetch(this.url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
      body: JSON.stringify({
        task: this.task
      })
    })
    .then(response => response.json())
    .then((data) => {
      this.todos.push(data)
      this.task = ''
      this.$refs.task.focus()
    })
  },

  // Marca a tarefa como feita ou não.
  toggleDone(todo) {
    fetch(`/todo/api/v1/${todo.id}/done/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
      body: JSON.stringify({
        done: !todo.done
      })
    })
    .then(response => response.json())
    .then((data) => {
      if (data.success) todo.done = !todo.done
    })
  },

  deleteTask(todo) {
    fetch(`/todo/api/v1/${todo.id}/delete/`, {
      method: 'DELETE',
    })
    .then(response => response.json())
    .then((data) => {
      if (data.success) {
        this.todos.splice(this.todos.indexOf(todo), 1)
      }
    })
  }
})