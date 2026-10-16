---
name: interago-noticias
description: >-
  Cria e edita artigos de notícias/blog e Web Stories de um site Interago
  pela API: rascunho, título, capa, tag, autor, publicação. Use quando a
  pessoa pedir para escrever ou publicar um post, notícia, matéria, artigo de
  blog ou web story.
---

# Notícias e Web Stories

Pré-requisito: `interago-api`. Notícias precisa da extensão Notícias; Web Stories da extensão Web Stories (`NEWS_EXTENSION_REQUIRED` / `WEBSTORIES_EXTENSION_REQUIRED` se faltar).

## 1. Artigo

```bash
python3 scripts/interago_api.py loja news listAuthors
python3 scripts/interago_api.py loja news listTags
python3 scripts/interago_api.py loja news listArticles status=0,1 page=1 pageSize=20
python3 scripts/interago_api.py loja news getArticle publishNewsId=ID includeVirtual=1 --out workspace/loja/noticias/ID.json
```

Status: `0` rascunho, `1` publicado, `2` inativo. Artigo inativo não se edita pela API: reative no painel.

**Corpo do artigo:** `articleJson` é o JSON do editor do painel. O jeito mais seguro de montar é partir de um artigo existente (`getArticle includeVirtual=1`), copiar a estrutura e trocar o texto.

```bash
python3 scripts/interago_api.py loja news proposeArticleDraft publishNewsId=new authorUserId=AUTOR articleJson=@workspace/loja/noticias/novo.json
python3 scripts/interago_api.py loja news applyArticleDraft   publishNewsId=new authorUserId=AUTOR articleJson=@workspace/loja/noticias/novo.json
```

- Artigo novo exige `authorUserId` (um `userId` de `listAuthors`).
- Em artigo já publicado, a alteração fica no rascunho até republicar no painel. O publicado continua no ar como estava.

**Título, capa, tag, SEO:**

```bash
python3 scripts/interago_api.py loja news proposeArticleMeta publishNewsId=ID title="..." subtitle="..." image=URL tagId=TAG titleTag="..." titleSocial="..."
python3 scripts/interago_api.py loja news applyArticleMeta   publishNewsId=ID title="..." subtitle="..." image=URL tagId=TAG titleTag="..." titleSocial="..."
```

Capa: URL do Media Center (`listMedia`, campo `cdnUrl`). Veja `interago-seo-midia`.

**Publicar:**

1. `applyArticleStatus publishNewsId=ID status=1` tira do rascunho e atualiza o sitemap de notícias. Confirme antes (grava direto). Bloqueado na loja grátis.
2. O HTML da matéria vai ao ar no painel: **Notícias → Atualizar**.
3. Link: `getArticle` → `publicUrl`. Janela anônima.

Texto: só o que a pessoa deu ou aprovou. Não invente fato, número, citação nem fonte. Um `h1` (o título), subtítulos em `h2`/`h3`.

## 2. Web Stories

```bash
python3 scripts/interago_api.py loja webstories getWebstoriesConfig
python3 scripts/interago_api.py loja webstories listWebstories page=1 pageSize=20
python3 scripts/interago_api.py loja webstories getWebstory webstoryId=ID includePages=1 --out workspace/loja/stories/ID.json
python3 scripts/interago_api.py loja webstories proposeWebstory webstoryId=new title="..." description="..." image=URL pages=@workspace/loja/stories/novo.json
python3 scripts/interago_api.py loja webstories applyWebstory   webstoryId=new title="..." description="..." image=URL pages=@workspace/loja/stories/novo.json
python3 scripts/interago_api.py loja webstories applyWebstoryPublish webstoryId=ID
```

- `pages` é o JSON do editor; parta de uma story existente.
- Imagens do Media Center (`listMedia`).
- `applyWebstory` só grava. `applyWebstoryPublish` envia ao site e exige o caminho configurado em Configurações da extensão.
- Republicar a lista ou uma story: `applyWebstoriesRefresh` (com ou sem `webstoryId`).
- `deleteWebstory` apaga só rascunho. Publicada se remove no painel.
- Link: `getWebstoriesConfig` traz o endereço da lista; a story publicada tem a URL pública no `getWebstory`.

## 3. Layouts

Modelo visual do portal (capa, matéria, tag, autor, AMP): `interago-layouts`.

## 4. Se a API não deixar

| Situação | Caminho |
|---|---|
| Extensão não instalada | Instalar no painel (Extensões). Na grátis, extensão nova pede Upgrade. |
| `FREE_TIER_DENIED` ao publicar | Painel: abrir a matéria em Notícias → publicar → Notícias → Atualizar. |
| `WEBSTORY_PUBLISHED` ao apagar | Painel, em Web Stories. |
| Formato do `articleJson` recusado | Entregue o texto em arquivo; a pessoa cola no editor de Notícias e publica. |

Artigos da Central de Ajuda sobre blog e notícias: `skills/interago-suporte/ajuda/` (procure "notícias" e "blog" no índice).
