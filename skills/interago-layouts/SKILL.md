---
name: interago-layouts
description: >-
  Lê e altera os layouts de catálogo (home, listagem, produto, menu, busca) e
  de notícias de uma loja Interago pela API, com validação e histórico. Use
  quando a pessoa quiser mudar a vitrine, a página de produto, a listagem, a
  busca ou o modelo das notícias, ou quando a API responder
  LAYOUT_STAFF_REQUIRED.
---

# Layouts de catálogo e notícias

Pré-requisitos: `interago-api` e `interago-html-padrao`.

## 1. Quem pode

Todos os métodos de layout (ler, validar, gravar) pedem token de **administrador** da loja ou da equipe Interago. Token de lojista comum recebe `403 LAYOUT_STAFF_REQUIRED`.

Se vier esse erro: pare. Explique que o layout do catálogo é uma área protegida, porque um erro derruba a vitrine inteira. Saídas: um administrador da conta gera o token, ou o suporte do Interago faz a alteração. Ofereça entregar o código pronto em arquivo.

Na loja grátis, gravar layout também é bloqueado (`FREE_TIER_DENIED`).

## 2. Tipos

| Layout de catálogo (`type`) | Página |
|---|---|
| `home` | Vitrine inicial do catálogo |
| `list` | Listagem e categoria |
| `product` | Página do produto |
| `menu` | Menu do catálogo |
| `data` | Dados auxiliares; em muitas lojas, a busca |

| Layout de notícias (`type`) | Página |
|---|---|
| `home` | Capa do portal |
| `web` | Matéria |
| `tag` | Página de tag |
| `author` | Página de autor |
| `data` | Dados auxiliares |
| `amp` | Versão AMP |
| `menu` | Menu |

Para achar a página de busca, produto ou listagem, use o layout. Não procure entre as páginas comuns (`listPages`).

## 3. Fluxo

```bash
python3 scripts/interago_api.py loja catalog getCatalogLayoutEngine
python3 scripts/interago_api.py loja catalog getCatalogLayout type=product --out workspace/loja/layouts/product.json
# edite workspace/loja/layouts/product.html
python3 scripts/interago_api.py loja catalog proposeCatalogLayout type=product code=@workspace/loja/layouts/product.html previewId=PRODUCT_ID
python3 scripts/interago_api.py loja catalog applyCatalogLayout   type=product code=@workspace/loja/layouts/product.html previewId=PRODUCT_ID
```

Notícias: `getNewsLayout` → `proposeNewsLayout` → `applyNewsLayout`, mesmos parâmetros (`previewId` é o ID do artigo, da tag ou do autor).

- `getCatalogLayoutEngine` diz qual motor a loja usa (legado ou template). Leia antes de editar, para escrever no formato certo.
- Baixe um tipo por vez, em arquivo. Não traga os cinco para o chat.
- `propose*` uma vez. Corrija pelos `errors`. Não fique tentando "para ver se passa".
- `compatible=false`: o código tem erro. Não grave.
- `compatible=true` com `previewAvailable=false`: o código está bom, só a prévia não montou (motivo em `warnings`). A gravação é permitida.
- O parâmetro é `code`.

## 4. Histórico e desfazer

```bash
python3 scripts/interago_api.py loja catalog listCatalogLayoutVersions type=product
python3 scripts/interago_api.py loja catalog getCatalogLayoutVersion type=product build=N --out workspace/loja/layouts/product-vN.json
```

Para voltar: baixe a versão boa e grave com `applyCatalogLayout`. `applyCatalogLayout` responde com `build` e `templatechangesId`; anote.

## 5. Publicar

Layout de catálogo gravado só aparece depois de atualizar o catálogo: `applyCatalogRefresh --autorizado` (com sim explícito) ou **Extensões → Catálogo → aba Atualizar**. Layout de notícias: **Notícias → Atualizar**.

Se várias alterações estão em andamento, atualize uma vez, no fim. Nunca no meio de uma série de gravações.

Mande o link da página afetada (`scripts/links.py loja produto ID`, `catalogo` ou `categoria ID`).

## 6. Não faça

- Não contorne layout de busca ou listagem com CSS ou JS em blocos (`catalogcss`, `catalogscripts`). A correção fica no layout.
- Não grave código com PHP solto ou trechos que o filtro de segurança recusa (`interago-waf`).
- Se a API recusar e você não achar a causa, entregue o código em arquivo. A pessoa (ou o suporte) cola no painel, no editor de layouts da extensão.
