---
name: interago-api
description: >-
  Base para operar projetos no Interago (loja ou site) através da API: formato da chamada,
  leitura das respostas e erros, ciclo propose/apply, limites, e a diferença
  entre gravado e publicado. Use sempre que for ler ou alterar algo no
  Interago via API (páginas, blocos, catálogo, notícias, SEO, mídia, pedidos,
  cupons, envios), ou quando a API devolver um erro que você precise
  interpretar.
---

# Interago API: a base

Leia depois de `interago-comecar`. As skills de cada área partem daqui.

## 1. Vocabulário

| Termo | O que é |
|---|---|
| **websiteId** | Número da loja/site. Toda chamada leva. |
| **token** | Chave da loja, de um usuário. Segredo. Fica em `.env.sites`. |
| **módulo** | Área: `pages`, `catalog`, `news`, `webstories`, `seo`, `media`, `orders`, `coupons`, `shipping`, `visits`, `account`. |
| **método** | A ação: `getBlock`, `applyProduct`, `listOrders`… |
| **painel** | app.interago.com.br. Tudo que a API faz existe lá, e muita coisa só lá. |
| **gravar** | Salvar no banco do Interago. |
| **publicar / atualizar** | Levar o que está gravado para o site que o visitante vê. Quase sempre é um passo separado. |

## 2. A chamada

```text
POST https://app.interago.com.br/App/Api/index.php
Authorization: Bearer TOKEN
Content-Type: application/x-www-form-urlencoded

websiteId=12345&module=catalog&method=getProduct&productId=987
```

Use o cliente do repositório:

```bash
python3 scripts/interago_api.py minhaloja catalog getProduct productId=987
python3 scripts/interago_api.py minhaloja pages getBlock blockinwebsiteId=123 includeContent=1 --out workspace/minhaloja/blocos/123.json
python3 scripts/interago_api.py minhaloja pages proposeBlockContent blockinwebsiteId=123 content=@workspace/minhaloja/blocos/123-header.html
```

- `chave=@arquivo` envia o conteúdo do arquivo. Use para HTML e JSON grandes.
- `--out` salva a resposta inteira; o terminal mostra só um resumo.
- Parâmetro JSON (`items`, `variations`, `operations`, `filters`, `fields`) vai como texto JSON.
- O cliente lê a cota antes de cada chamada (`account.getUsage`, grátis) e para se a cortesia acabou.

## 3. Lendo a resposta

Sucesso é sempre `"status": "success"`.

```json
{ "status": "success", "module": "catalog", "method": "getProduct", "product": { "productId": 987, "publicUrl": "https://..." } }
```

Erro:

```json
{ "status": "error", "code": "CATEGORY_URL_CONFLICT", "message": "url já usada por outra categoria nesta loja.", "http": 422 }
```

1. Decida pelo **`code`**. A frase pode mudar.
2. Leia `warnings` mesmo no sucesso. É ali que a API avisa que ignorou ou ajustou algo.
3. Listagens: `page`, `pageSize` (máx. 50 na maioria; 100 em medidas), `hasMore`. Pare quando `hasMore` for `false`.
4. `success` prova que a API aceitou. Não prova que o visitante já vê (seção 6).

Tabela de códigos: [referencia/erros.md](referencia/erros.md).

## 4. propose → apply

| Método | Faz | Grava? |
|---|---|---|
| `propose*` | Valida, devolve `errors`, `warnings`, às vezes prévia | Não |
| `apply*` | Grava | Sim |

```text
1. get*      estado atual, salvo em arquivo (não cole no chat)
2. editar    no arquivo, só o trecho necessário
3. propose*  uma vez; corrigir o que ela apontar
4. apply*    uma vez, depois que a pessoa confirmar
5. get*      conferir
6. publicar  no painel ou pela API, conforme a seção 6
7. link      mandar o endereço para a pessoa ver (scripts/links.py)
```

- Mostre o que vai mudar e peça o OK antes do `apply*`.
- Não chame `propose*` em loop. Leia o erro e corrija.
- Gravam sem propose: `createPage`, `createBlock`, `createCoupon`, `updateCoupon`, linhas de bloco, `deleteWebstory`, `applyArticleStatus`. Confirme antes.

**Loja grátis:** `get*`, `list*` e `propose*` funcionam. Gravar páginas, blocos, catálogo, frete, cupons e SEO volta `FREE_TIER_DENIED`. Então: leia, prepare o conteúdo, valide com `propose*`, e ensine a pessoa a aplicar pelo painel (`interago-suporte`), ou indique o Upgrade.

## 5. Escrita: nunca repetir às cegas

| Situação | Faça |
|---|---|
| `apply*` com 500, corpo vazio ou queda de rede | Não reenvie. Releia com `get*`. Só reaplique se não entrou. |
| `REFRESH_PENDING` (409) | Pare. Já tem atualização rodando. |
| 429 | Espere `retryAfterSeconds`. |
| 422 | Corrija pelo `errors` antes de qualquer `apply*`. |
| `PAYLOAD_REJECTED` | `interago-waf`. Não corte o conteúdo. |
| `FREE_TIER_DENIED` | Painel ou Upgrade. Não tente outro método para contornar. |
| `LAYOUT_STAFF_REQUIRED` | `interago-layouts`. |

## 6. Gravado não é publicado

| Você gravou | O visitante vê depois de |
|---|---|
| Produto, preço, estoque, variação, categoria | Atualizar o catálogo: `applyCatalogRefresh` (com OK) ou painel → Catálogo → Atualizar |
| Layout de catálogo | Atualizar o catálogo |
| Tags do produto | Na hora (a busca lê ao vivo) |
| Rascunho de página ou bloco | Painel: Publicar a página + Menu → Atualizar → Páginas (**Atualizar e Subir**). A API não publica páginas. |
| Artigo de notícia | `applyArticleStatus` + painel → Notícias → Atualizar |
| Web Story | `applyWebstoryPublish` (ou `applyWebstoriesRefresh` para republicar) |
| SEO da página | Painel → SEO → Atualizar e publicar a página |
| Faixa de CEP | Na próxima cotação de frete |
| Cupom | Em geral na hora |

**`applyCatalogRefresh` só com um sim explícito.** Recompila a loja inteira. Junte as alterações, peça o OK uma vez, chame uma vez. O cliente exige `--autorizado`.

Ao terminar, diga o que já está no ar, o que falta publicar e mande o link (`python3 scripts/links.py APELIDO ...`). O passo a passo do painel está em `interago-suporte`.

## 7. Limites

- 60 chamadas por minuto por loja. Estourar pode bloquear a API (`API_BLOCKED`, só o suporte libera).
- Cortesia de 100 chamadas por mês sem faturamento.
- Leituras: 2 ou 3 em paralelo, no máximo. Escritas: uma por vez.
- Conte antes: 40 produtos × (propose + apply) = 80 chamadas. Use os lotes (`applyProductPrices`, `applyProductStocks`, `applyProductMeasuresBatch`, até 100 itens).

## 8. Economize contexto

- Respostas grandes vão para arquivo (`--out`). Não cole HTML inteiro no chat.
- `getBlock` com `includeContent=0` quando só precisa do nome e da variante.
- Trecho de bloco: `operations` (localizar/substituir), não o HTML todo.
- Muitas mudanças: cópia local com `python3 scripts/snapshot.py APELIDO` (só se a cota permitir).

## 9. Confirme o alvo antes de gravar

1. Loja (apelido).
2. Tipo: página, bloco, produto, categoria, layout, artigo, SEO, cupom, frete.
3. ID, descoberto com `list*`/`get*`. Não adivinhe.
4. O que muda, e se é só validar ou validar e gravar.

## 10. Referência

- Todos os métodos com parâmetros: [referencia/metodos.md](referencia/metodos.md).
- `account.getUsage`: cota do mês e do minuto. Não gasta cota.
- Lista viva: https://app.interago.com.br/App/Api/panel/moduleMethods.js
- Testador de cada método no painel, em **API Interago**.
- Artigos da API na Central de Ajuda: `skills/interago-suporte/ajuda/api.md`.

## Skills por área

| Preciso… | Skill |
|---|---|
| Publicar, ver no site, usar o painel, suporte | `interago-suporte` |
| Página, bloco, header, footer, banner | `interago-paginas-blocos` |
| Produto, categoria, preço, estoque, variação, +Campos, tags | `interago-catalogo` |
| Layout de catálogo ou notícias | `interago-layouts` |
| Notícias e Web Stories | `interago-noticias` |
| SEO e Media Center | `interago-seo-midia` |
| Pedidos, cupons, frete, relatórios | `interago-pedidos-envios` |
| HTML e CSS no padrão da plataforma | `interago-html-padrao` |
| `PAYLOAD_REJECTED` | `interago-waf` |
