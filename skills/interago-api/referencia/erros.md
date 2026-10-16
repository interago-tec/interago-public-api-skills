# Erros da API Interago e o que fazer

Decida pelo `code`, não pela frase. A resposta de erro traz `status` diferente de `success`, o `code` e, em geral, `message`, `hint`, `errors` e `warnings`. O cliente deste repositório acrescenta `http` com o status HTTP.

Regra geral:

- **4xx**: o pedido está errado ou não é permitido. Corrija o pedido ou explique o limite à pessoa. Não repita igual.
- **5xx em leitura**: pode tentar de novo depois de alguns segundos (o cliente já tenta até 3 vezes).
- **5xx em escrita (`apply*`, `create*`, `update*`, `delete*`)**: não repita. Releia com `get*`. A escrita pode ter entrado.

## Acesso, plano e limites

| Código | HTTP | Significa | O que fazer |
|---|---|---|---|
| `TOKEN_REQUIRED`, `TOKEN_USE_BEARER` | 401 | Token ausente ou fora do cabeçalho | O token vai só em `Authorization: Bearer`. Confira o `.env.sites`. |
| `TOKEN_INVALID` | 401 | Token errado ou trocado | Peça para gerar outro na tela API Interago e atualizar o `.env.sites`. Gerar novo invalida o antigo. |
| `LEGACY_HEADER_REMOVED` | 401 | Cabeçalho antigo `X-Api-Token` | Use `Authorization: Bearer`. |
| `API_DISABLED` | 403 | API desligada nesta loja | Painel → API Interago → ligar **API ativa** → Salvar. |
| `API_BLOCKED` | 403 | API bloqueada (excesso por minuto) | Só a equipe do Interago desbloqueia. Oriente a falar com o suporte. Não insista. |
| `API_QUOTA_EXCEEDED` | 403 | Cortesia de 100 chamadas do mês acabou | Mande à pessoa o `upgradeUrl` da resposta. Upgrade ou faturamento Interago, ou esperar o dia 1º. Veja `interago-comecar`. |
| `RATE_LIMITED` | 429 | Mais de 60 chamadas no minuto | Espere `retryAfterSeconds` (~60 s) e diminua o ritmo. |
| `SERVER_BUSY` | 429 | A API inteira está no limite operacional | Espere `retryAfterSeconds`. Em escrita, releia antes de repetir. |
| `FREE_TIER_DENIED` | 403 | Loja grátis: a API não grava | Não é erro do pedido. Ensine a fazer pelo painel (skill `interago-suporte`) ou indique Upgrade. |
| `FREE_TIER_PRODUCT_LIMIT` | 403 | Teto de produtos da loja grátis | Upgrade para cadastrar mais. |
| `*_EXTENSION_REQUIRED` | 403 | A extensão daquele módulo não está instalada (`CATALOG_`, `NEWS_`, `SEO_`, `SHIPPING_`, `VISITS_`, `WEBSTORIES_`) | Instalar a extensão no painel. Na grátis, extensão nova é bloqueada: Upgrade ou suporte. |
| `LAYOUT_STAFF_REQUIRED` | 403 | Layout de catálogo/notícias só para equipe Interago ou administrador | Pare. Explique. Veja `interago-layouts`. |
| `MODULE_METHOD_REQUIRED`, `WEBSITE_REQUIRED` | 400 | Faltou `module`, `method` ou `websiteId` | Corrija a chamada. |
| `METHOD_UNKNOWN` | 404 | Módulo ou método não existe | Confira o nome em `metodos.md` ou na lista viva. |

## Conteúdo recusado

| Código | HTTP | Significa | O que fazer |
|---|---|---|---|
| `PAYLOAD_REJECTED` | 403 | Filtro de segurança recusou o conteúdo | **Não é tamanho.** Siga `interago-waf`. Não corte o HTML. |
| `BLOCK_INCOMPATIBLE` | 422 | Bloco inválido, geralmente acima de 40.000 caracteres | Reduza o bloco (separe CSS em outro bloco) ou corrija o que `errors` apontar. |
| `BLOCK_UNCHANGED` | 409 | Conteúdo igual ao atual | Já está gravado. Não é falha. |
| `DRAFT_INCOMPATIBLE`, `DRAFT_FORBIDDEN_CONTENT` | 422 | Rascunho de página inválido | Leia `errors`. Confira `<iBlock>` (uma linha, `name` e `bw` reais). |
| `VIRTUAL_CONTENT_MANAGED` | 422 | Você mandou `virtualContent` | Nunca envie. A API gera. |
| `LAYOUT_INCOMPATIBLE`, `LAYOUT_PHP_TAG_NOT_ALLOWED`, `LAYOUT_PHP_API_DISABLED`, `LAYOUT_MALWARE_BLOCKED` | 4xx | Layout recusado | Veja `interago-layouts`. |

## Catálogo

| Código | HTTP | O que fazer |
|---|---|---|
| `PRODUCT_NOT_FOUND`, `CATEGORY_NOT_FOUND` | 404 | ID errado ou de outra loja. Liste antes (`listProducts`, `listCategories`). |
| `PRODUCT_INCOMPATIBLE`, `STOCK_INCOMPATIBLE`, `FILTERS_INCOMPATIBLE`, `TAGS_INCOMPATIBLE`, `VARIATIONS_INCOMPATIBLE` | 422 | Leia `errors` campo a campo. |
| `SKU_CONFLICT`, `SKU_AMBIGUOUS` | 422 | SKU já usado ou repetido. Escolha outro ou identifique por `productId`. |
| `PRODUCT_HAS_NESTED_VARIATIONS` | 422 | Produto com combinações. A API não altera: faça no painel. |
| `CATEGORY_ROOT_FORBIDDEN` | 4xx | A categoria raiz da loja não muda. |
| `CATEGORY_URL_CONFLICT` | 422 | URL `/cat/...` já usada. Outra URL. |
| `IDENTIFY_BY_INVALID`, `ITEMS_REQUIRED`, `ITEMS_EMPTY`, `ITEMS_INVALID`, `DUPLICATE_ITEM` | 400 | Lote mal montado. `identifyBy` = `productId` ou `sku`; `items` JSON com até 100. |
| `REFRESH_PENDING` | 409 | Já tem atualização do catálogo rodando. Espere. Não repita. |
| `CONFIG_NOT_FOUND` | 404 | Catálogo sem configuração. Peça para abrir Extensões → Catálogo → Config no painel. |

## Páginas e blocos

| Código | HTTP | O que fazer |
|---|---|---|
| `PAGE_URL_EXISTS` | 409 | Já existe página com esse link. Outro link ou edite a existente. |
| `BLOCK_NAME_EXISTS` | 409 | Já existe bloco com esse nome. Use o existente (`listBlocks`). |
| `VARIANT_NOT_EDITABLE`, `VARIANT_NOT_FOUND` | 4xx | Use uma variante de `listBlockVariants`. |
| `REPETITION_NOT_READY` | 422 | Bloco de repetição sem linhas. Mande o HTML modelo por `applyBlockContent` (`content`). |
| `LINE_LAST_FORBIDDEN` | 422 | Não dá para apagar a última linha. |
| `LINE_IDS_MISMATCH`, `LINE_IDS_DUPLICATE` | 422 | `reorderBlockLines` exige todos os `lineId`, sem repetir. |
| `LINE_LIMIT_EXCEEDED`, `COUNT_TOO_HIGH` | 4xx | Máx. 20 linhas por chamada e 100 no bloco. |

## Notícias, SEO, envios, pedidos

| Código | HTTP | O que fazer |
|---|---|---|
| `AUTHOR_REQUIRED`, `AUTHOR_INVALID` | 422 | Artigo novo precisa de `authorUserId` de `listAuthors`. |
| `DRAFT_EMPTY` | 409 | Publicar sem rascunho. Grave o rascunho antes. |
| `ESSENTIALS_REQUIRED` | 409 | Preencha os dados fixos (`updateEssentials`) antes do SEO de página. |
| `TOGGLE_PREREQUISITE_MISSING` | 422 | Faltam dados fixos para ligar aquele schema. A resposta diz quais. |
| `INVALID_URL`, `INVALID_IMAGE_URL` | 422 | URL precisa ser `https://` válida. |
| `CEP_RANGES_INVALID`, `MEASURES_INVALID` | 422 | Leia `errors`. Proponha antes de gravar. |
| `MULTIPLE_ELIGIBLE_ORDERS` | 4xx | Mais de um pedido para o documento. Informe `orderId`. |
| `ORDER_NOT_FOUND` | 404 | Rastreio só em pedido elegível (status 3 a 5). |
| `WEBSTORY_PUBLISHED` | 409 | Story publicada não se apaga pela API. Painel. |

## Corpo vazio, JSON quebrado, sem resposta

O cliente devolve `EMPTY_BODY` ou `TRANSPORT`. É falha de rede ou de servidor, não resposta da API. Em escrita, releia o estado antes de repetir.
