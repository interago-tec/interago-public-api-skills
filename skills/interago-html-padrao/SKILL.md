---
name: interago-html-padrao
description: >-
  Padrão de HTML, CSS e JS para páginas, blocos e layouts Interago: grade
  bootstrapGrid (container, row, col), HTML semântico para o Google, CSS sem
  !important no lugar certo, e as regras de JS que o Interago exige. Use
  sempre que for escrever ou revisar HTML, CSS ou JS para enviar à API ou
  colar no painel.
---

# HTML, CSS e JS no padrão Interago

## 1. Grade: bloco `bootstrapGrid`

Todo site Interago já traz um bloco chamado `bootstrapGrid` com a grade e utilitários. Use. Não importe Bootstrap de CDN nem crie outro grid. Não copie nem edite esse bloco.

```html
<section class="my-5">
  <div class="container">
    <div class="row">
      <div class="col-12 col-md-6">…</div>
      <div class="col-12 col-md-6">…</div>
    </div>
  </div>
</section>
```

- Sempre `container` → `row` → `col-*`. Coluna fora de `row` quebra.
- `.row` é CSS Grid de 12 colunas, espaço de 20px.
- Colunas: `col-*`, `col-sm-*` (≥576), `col-md-*` (≥768), `col-lg-*` (≥992), `col-xl-*` (≥1200), `col-xxl-*` (≥1400).
- `.container` vai até 1620px de largura em telas ≥1460px.

Utilitários (escala 0 / 5 / 10 / 15 / 30 / 60 px, sufixos `-0` a `-5`):

| Classe | Efeito |
|---|---|
| `my-*` | padding em cima e embaixo (é padding, não margin) |
| `mt-*` `mb-*` `ml-*` `mr-*` | margin |
| `py-*` `pt-*` `pb-*` `pl-*` `pr-*` | padding |
| `my-lg-*` `mt-lg-*` `mb-lg-*` `ml-lg-*` `mr-lg-*` | a partir de 992px |
| `text-left` `text-center` `text-right` | alinhamento |

Não existem: `px-*`, `mx-*`, `d-flex`, `justify-content-*`, `g-*`. Precisou, escreva CSS próprio.

## 2. HTML semântico

O Google lê o HTML final: header + página + footer.

| Peça | Tag |
|---|---|
| Topo, logo | `<header>` (bloco header) |
| Menu | `<nav>` |
| Conteúdo da página | `<main>`, uma vez, no rascunho da página |
| Seção temática | `<section>` com título |
| Post, card autônomo | `<article>` |
| Conteúdo lateral | `<aside>` |
| Rodapé | `<footer>` (bloco footer) |

- **Um `<h1>` por página**, com o assunto da página (não o logo). Depois `h2`, `h3`, sem pular nível.
- Título não é tamanho de fonte. Tamanho é CSS.
- Parágrafo em `<p>`, listas em `<ul>`/`<ol>`, ênfase em `<strong>`/`<em>`.
- Link com texto que diz o destino. Nada de "clique aqui" sozinho.
- Toda `<img>` com `alt`. Decorativa: `alt=""`. Logo: o nome da empresa.
- Na listagem do catálogo, o nome da categoria é o `h1`; os cards não.
- Oferta, cupom e chamada de compra em texto HTML, não só dentro de imagem.

## 3. CSS

- **Sem `!important`.** Se a regra não pega, aumente a especificidade (`#secao .titulo`) ou coloque depois da regra que perde.
- **Lugar certo:**
  - global (cores, fontes, header, footer, utilitários da marca): bloco `customCSS` (ou o bloco de CSS global da loja);
  - só daquela página: no rascunho da página ou no bloco da seção.
  - Não repita a mesma regra nos dois.
- Header e footer guardam HTML. O CSS deles vai no global.
- Variáveis de cor em `:root` no CSS global; reuse.
- Copy sem travessão como pausa.

## 4. JS

Regras do Interago, que quebram o site ou a API se ignoradas:

1. **Nunca `//` em JS** de página ou bloco: nem comentário de linha, nem `https://` literal. O Interago corta o script ali. Comentário só `/* … */`. URL: `'https:' + '/' + '/' + 'dominio.com'`.
2. **Sem crase (template literal)**, `eval(`, `.exec(`, `${…}`, `{{…}}`. O filtro da API recusa a requisição (`interago-waf`).
3. Prefira CSS para interação simples (abas com `:checked`, `<details>` para FAQ).
4. Carregar HTML de outro lugar: `fetch` + `DOMParser` + `appendChild`, não `innerHTML` com HTML de fora.

## 5. iBlock

```html
<iBlock name="header" bw="1234"/>
```

- Uma linha só.
- `name` e `bw` de um bloco real desta loja (confira com `getBlock`).
- Para escrever o texto `<iBlock` dentro de uma ilustração ou exemplo, quebre a tag (por exemplo, com um caractere invisível depois do `<`). Senão o Interago tenta montar o bloco.

## 6. Antes de enviar

- [ ] `container` → `row` → `col-*`
- [ ] Um `h1`, níveis em ordem
- [ ] `alt` em toda imagem
- [ ] Sem `!important`
- [ ] CSS no lugar certo, sem duplicar
- [ ] JS sem `//`, sem crase, sem `eval(`
- [ ] Bloco abaixo de 40.000 caracteres
- [ ] Testado no celular depois de publicar (o link da página, em janela anônima)
