(function () {
  var raiz = document.documentElement;

  // tema claro/escuro
  var botaoTema = document.querySelector('[data-tema]');
  if (botaoTema) {
    botaoTema.addEventListener('click', function () {
      var escuro = raiz.dataset.theme ? raiz.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
      raiz.dataset.theme = escuro ? 'light' : 'dark';
      try { localStorage.setItem('tema', raiz.dataset.theme); } catch (e) {}
    });
  }

  // menu no celular
  var menu = document.querySelector('[data-menu]');
  var lateral = document.querySelector('[data-lateral]');
  if (menu && lateral) {
    menu.addEventListener('click', function () {
      var aberta = lateral.classList.toggle('aberta');
      menu.setAttribute('aria-expanded', aberta ? 'true' : 'false');
    });
  }
  var atual = document.querySelector('.lateral [aria-current]');
  if (atual && lateral) lateral.scrollTop = atual.offsetTop - lateral.clientHeight / 2;

  // copiar código
  document.querySelectorAll('.hl, .corpo > pre').forEach(function (bloco) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'copiar';
    b.textContent = 'Copiar';
    b.addEventListener('click', function () {
      var texto = bloco.querySelector('code') ? bloco.querySelector('code').innerText : bloco.innerText;
      navigator.clipboard.writeText(texto).then(function () {
        b.textContent = 'Copiado';
        setTimeout(function () { b.textContent = 'Copiar'; }, 1500);
      });
    });
    bloco.appendChild(b);
  });

  // nesta página: destaca a seção visível
  var links = Array.prototype.slice.call(document.querySelectorAll('.toc a'));
  if (links.length && 'IntersectionObserver' in window) {
    var porId = {};
    links.forEach(function (a) { porId[decodeURIComponent(a.hash.slice(1))] = a; });
    var obs = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (e) {
        if (e.isIntersecting && porId[e.target.id]) {
          links.forEach(function (a) { a.classList.remove('on'); });
          porId[e.target.id].classList.add('on');
        }
      });
    }, { rootMargin: '-70px 0px -70% 0px' });
    Object.keys(porId).forEach(function (id) { var h = document.getElementById(id); if (h) obs.observe(h); });
  }

  // busca
  var campo = document.querySelector('[data-busca]');
  var lista = document.querySelector('[data-resultados]');
  if (!campo || !lista) return;
  var base = campo.dataset.raiz || '';
  var indice = null;
  var sel = -1;
  function carregar() {
    if (indice) return Promise.resolve(indice);
    return fetch(base + 'assets/busca.json').then(function (r) { return r.json(); }).then(function (d) { indice = d; return d; });
  }
  function norm(s) { return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }
  function mostrar(itens, termo) {
    lista.innerHTML = '';
    sel = -1;
    if (!termo) { lista.hidden = true; return; }
    if (!itens.length) {
      lista.innerHTML = '<li class="vazio">Nenhuma dica encontrada. Tente outra palavra.</li>';
    }
    itens.slice(0, 12).forEach(function (it) {
      var li = document.createElement('li');
      var a = document.createElement('a');
      a.href = base + it.s + '/';
      a.textContent = (it.n ? 'Dica ' + it.n + ': ' : '') + it.t;
      var small = document.createElement('small');
      small.textContent = it.c;
      a.appendChild(small);
      li.appendChild(a);
      lista.appendChild(li);
    });
    lista.hidden = false;
  }
  campo.addEventListener('input', function () {
    var termo = norm(campo.value.trim());
    carregar().then(function (d) {
      var palavras = termo.split(/\s+/).filter(Boolean);
      var res = d.map(function (it) {
        var t = norm(it.t), x = norm(it.x);
        var pontos = 0;
        for (var i = 0; i < palavras.length; i++) {
          var p = palavras[i];
          if (t.indexOf(p) >= 0) pontos += 10;
          else if (x.indexOf(p) >= 0) pontos += 1;
          else return null;
        }
        return { it: it, p: pontos };
      }).filter(Boolean).sort(function (a, b) { return b.p - a.p; }).map(function (r) { return r.it; });
      mostrar(res, termo);
    });
  });
  campo.addEventListener('keydown', function (e) {
    var itens = lista.querySelectorAll('a');
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault();
      sel = Math.max(0, Math.min(itens.length - 1, sel + (e.key === 'ArrowDown' ? 1 : -1)));
      itens.forEach(function (a, i) { a.classList.toggle('ativo', i === sel); });
    } else if (e.key === 'Enter' && itens[sel >= 0 ? sel : 0]) {
      location.href = itens[sel >= 0 ? sel : 0].href;
    } else if (e.key === 'Escape') {
      campo.value = ''; mostrar([], '');
    }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === '/' && document.activeElement !== campo) { e.preventDefault(); campo.focus(); }
  });
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.busca')) lista.hidden = true;
  });
})();
