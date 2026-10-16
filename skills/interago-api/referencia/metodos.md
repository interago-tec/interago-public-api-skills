# Métodos da API Interago

Gerado por `scripts/atualizar_metodos.py` a partir de https://app.interago.com.br/App/Api/panel/moduleMethods.js.
Se um método não estiver aqui, ele é mais novo que esta cópia: consulte a fonte.

## `orders`: Pedidos

Módulo orders — pedidos, rastreio e consultas por documento.

| Método | O que faz | Parâmetros |
|---|---|---|
| `getOrder` | Detalhes completos de um pedido por orderId (cliente PF/PJ com CNPJ, itens, frete, pagamento, rastreio). | orderId (obrig.) |
| `listOrders` | Lista pedidos paginados por intervalo de datas e status (padrão status 3–6). | dateFrom, dateTo (obrig.), status, page, pageSize |
| `listOrdersByDocument` | Lista pedidos de um CPF/CNPJ no intervalo informado, paginado. | document, dateFrom, dateTo (obrig.), status, page, pageSize |
| `addTrackingCodeToOrder` | Envia código de rastreio para pedido elegível (status 3–5) e marca como Enviado (6). Por documento: exige pedido único; se houver vários, retorna MULTIPLE_ELIGIBLE_ORDERS. | trackingCode (obrig.), trackingUrl, orderId ou document |

## `coupons`: Cupons

Módulo coupons — extensão 11 (Cupons). Criar, listar, consultar e atualizar cupons da loja. discountType é value ou percent. useLimit e useLimitPerPerson mínimos 1. Sem accountIds o cupom vale para a loja inteira; com contas ou includeDocuments fica restrito. code não muda no update. Mutações bloqueadas em loja free-tier.

| Método | O que faz | Parâmetros |
|---|---|---|
| `listCoupons` | Lista cupons agrupados por code (ativo, expirado, agendado ou todos). | status (all/active/expired/scheduled), code, page, pageSize |
| `getCoupon` | Detalhe de um cupom: público, documentos mascarados, escopo e últimos usos. | couponId ou code |
| `checkCouponCode` | Diz se o code já existe nesta loja. | code (obrig.) |
| `createCoupon` | Cria o cupom. Sem code, a API gera um código de 6 caracteres. Várias accountIds geram uma linha por conta, no mesmo code. | discountValue, discountType, useLimit, useLimitPerPerson, startDate, endDate (obrig.) |
| `updateCoupon` | Atualiza o cupom e todas as linhas do mesmo code. Campos omitidos permanecem. code não muda. | couponId (obrig.) + campos a alterar |

## `shipping`: Envios / Logística

Módulo shipping — extensão 9 (Envios). Faixas de CEP para entrega própria (listCepRanges / proposeCepRanges / applyCepRanges) e medidas de frete por produto (ProductMeasures). Em applyCepRanges, mode=replace substitui todas as faixas; append acrescenta. A ordem das faixas importa na cotação. Peso do produto continua no módulo catalog (applyProduct). Mutações bloqueadas em loja free-tier.

| Método | O que faz | Parâmetros |
|---|---|---|
| `listCepRanges` | Lista as faixas de CEP cadastradas na loja (mesma base do painel Envios → Faixas). | — |
| `proposeCepRanges` | Valida o JSON das faixas sem gravar. Use antes de apply para ver erros e o preview ordenado. | cepRanges (JSON array obrig.), mode (replace/append, padrão replace) |
| `applyCepRanges` | Grava as faixas de CEP. Valem na próxima cotação de frete (sem republicar o catálogo). replace com [] limpa todas. | cepRanges (JSON array obrig.), mode (replace/append, padrão replace) |
| `getShippingDefaults` | CEP da loja e medidas padrão usadas quando o produto não tem ProductMeasures. | — |
| `listProductMeasures` | Lista produtos com medidas de frete (paginado). | page, pageSize (máx. 100), onlyWithMeasures (0/1), search |
| `getProductMeasures` | Medidas de frete de um produto (ou defaults se ainda não tiver tabela própria). | productId (obrig.) |
| `proposeProductMeasures` | Valida width/height/length/fragile sem gravar. | productId, width, height, length (obrig.), fragile (0/1) |
| `applyProductMeasures` | Grava medidas de frete do produto (ProductMeasures). | productId, width, height, length (obrig.), fragile (0/1) |
| `applyProductMeasuresBatch` | Grava medidas em lote (máx. 100 itens). identifyBy=productId ou sku. | items (JSON array obrig.), identifyBy (productId/sku) |
| `deleteProductMeasures` | Remove as medidas próprias do produto (volta aos defaults da loja). | productId (obrig.) |

## `visits`: Relatórios

Módulo visits — os mesmos relatórios de #visit.main (ext. 1). listReports lista o catálogo e a disponibilidade; getReport devolve os dados do gráfico/tabela.

| Método | O que faz | Parâmetros |
|---|---|---|
| `listReports` | Lista os relatórios da tela Relatórios, com periodType e se estão disponíveis neste site (loja/blog). | — |
| `getReport` | Retorna os dados de um relatório (mesmo payload de #visit.main). period padrão: thisMonth ou thisYear conforme o relatório. | report (obrig.), period, filter |

## `catalog`: Catálogo

Módulo catalog — produtos, categorias, marcas, variações e tags (ext. 5). Alterações de produto/estoque/variações exigem applyCatalogRefresh para refletir no site. Tags do produto (applyProductTags) não disparam refresh: a busca lê ProductTag ao vivo. Variações na API v1 são opções planas (sem combinações aninhadas). Métodos de layout exigem equipe Interago (userType 1) ou administrador (userType 2); token de lojista ou legado recebe 403 LAYOUT_STAFF_REQUIRED.

| Método | O que faz | Parâmetros |
|---|---|---|
| `listProducts` | Lista produtos paginados (categoria, status, marca, busca). | categoryId, brandId, status (0/1), search, page, pageSize |
| `getProduct` | Detalhe do produto; includeStock/includeBrand/includeTags opcionais. | productId (obrig.), includeStock, includeBrand, includeTags |
| `listCategories` | Categorias do catálogo (paginado). | parentId, search, page, pageSize |
| `getCategory` | Detalhe de uma categoria. | categoryId (obrig.) |
| `proposeCategory` | Valida criação/edição de categoria sem gravar. Raiz (parentId=0) não pode ser alterada. URL pública sempre /cat/{slug}. | categoryId (new ou id), name, parentId, description, image, url, googleCategoryName, visible, categoryJson… |
| `applyCategory` | Cria ou atualiza categoria (ext. 5). Raiz bloqueada; URL só /cat/{slug}; googleCategoryName vazio não apaga mapeamento. | categoryId (new ou id), name, parentId, description, image, url, googleCategoryName, visible, categoryJson… |
| `listBrands` | Marcas cadastradas (paginado). | search, page, pageSize |
| `listVariations` | Tipos planos da loja (parentId=0: Cor, Tamanho…), paginado. Cadastros globais, não opções de um produto. | search, page, pageSize |
| `getCatalogConfig` | Path e snippets globais do catálogo. | — |
| `proposeProduct` | Valida criação/edição de produto simples sem gravar. | productId (new ou id), title, price, sku, categoryId, additionalCategoryIds, productJson… |
| `applyProduct` | Cria ou atualiza produto simples (tipo 0), inclusive categorias adicionais. Resposta: status=success, productStatus=0/1, price persistido. | productId (new ou id), campos do produto, additionalCategoryIds |
| `proposeProductStatus` | Valida online/offline (0/1) sem gravar. | productId (obrig.), status (obrig.) |
| `applyProductStatus` | Ativa ou desativa produto. | productId (obrig.), status (obrig.) |
| `proposeProductStock` | Valida alteração de estoque (produto simples). | productId (obrig.), stockQty (obrig.) |
| `applyProductStock` | Atualiza estoque de produto simples. | productId (obrig.), stockQty (obrig.) |
| `proposeProductPrices` | Valida preços em massa (máx. 100) sem gravar. Variações só via sku. | identifyBy (productId/sku), items (JSON) |
| `applyProductPrices` | Aplica preços em massa (máx. 100). Sucesso parcial; no-ops em unchanged. | identifyBy (productId/sku), items (JSON) |
| `proposeProductStocks` | Valida estoques em massa (máx. 100) sem gravar. Variações só via sku. | identifyBy (productId/sku), items (JSON) |
| `applyProductStocks` | Aplica estoques em massa (máx. 100). Sucesso parcial; no-ops em unchanged. | identifyBy (productId/sku), items (JSON) |
| `getProductFilters` | Lê o valor atual dos +Campos de um produto (texto simples, texto rico, mídias e HTML). | productId (obrig.), filterIds (CSV, opcional) |
| `proposeProductFilters` | Valida o preenchimento de +Campos (ProductFilter) de um produto sem gravar. | productId (obrig.), filters (JSON) ou filterId+value |
| `applyProductFilters` | Grava +Campos (texto simples, texto rico, mídias ou HTML) de um produto. | productId (obrig.), filters (JSON) ou filterId+value |
| `getProductTags` | Lê as tags do produto (ProductTag), o mesmo campo do painel “Tags do Produto”. | productId (obrig.) |
| `proposeProductTags` | Valida o conjunto de tags sem gravar. Padrão replace (igual planilha). Lista vazia no replace remove todas. | productId (obrig.), tags ([a][b] ou JSON), mode (replace/merge) |
| `applyProductTags` | Grava tags em ProductTag. Replace: DELETE + INSERT. Não dispara applyCatalogRefresh (busca lê ao vivo). | productId (obrig.), tags (obrig.), mode (replace/merge) |
| `getProductVariations` | Lista tipos e opções de variação de um produto. hasNestedOptions=true indica combinações (API v1 não altera). | productId (obrig.) |
| `proposeProductVariations` | Valida criação/edição de opções planas sem gravar. SKU informado em conflito → erro. SKU vazio gera {skuProduto}-{slug}. Máx. 50 opções. | productId (obrig.), variations (JSON) |
| `applyProductVariations` | Upsert de opções planas (parentId=0). Não apaga opções omitidas. Marca productType=1 (quebra applyProductStock no pai). Recusa árvore aninhada. Depois: applyCatalogRefresh se online. | productId (obrig.), variations (JSON) |
| `applyCatalogRefresh` | Enfileira recompilação do catálogo (como botão Refresh do painel). | — |
| `getCatalogLayoutEngine` | Informa se a loja usa layout legado PHP ou template Enfine SaaS (.sass.html). Somente equipe Interago / administrador. | — |
| `getCatalogLayout` | Baixa o layout de catálogo (ext. 5) por type na última versão. Somente equipe Interago / administrador. | type (obrig.) |
| `listCatalogLayoutVersions` | Lista versões históricas do layout de catálogo por type. Somente equipe Interago / administrador. | type (obrig.) |
| `getCatalogLayoutVersion` | Baixa versão específica do layout de catálogo por type. Somente equipe Interago / administrador. | type (obrig.), templatechangesId ou build |
| `proposeCatalogLayout` | Valida alteração de layout sem gravar. Somente equipe Interago / administrador. Falha de preview (Config/dados) vem em warnings com compatible=true — não bloqueia o apply. Erro de PHP no code: compatible=false. | type, code (obrig.), previewId |
| `applyCatalogLayout` | Salva layout de catálogo. Somente equipe Interago / administrador (malware + PHP inválido também bloqueiam). Preview HTML indisponível não impede a gravação — igual ao painel. | type, code (obrig.), previewId |

## `news`: Notícias

Módulo news — leitura e rascunhos (ext. 4). Não publica no site automaticamente. Em rascunhos novos, informe authorUserId (userId retornado por listAuthors). A API grava o JSON virtual no mesmo formato do editor (parágrafos com encodeURIComponent). Métodos de layout exigem equipe Interago ou administrador (403 LAYOUT_STAFF_REQUIRED para os demais).

| Método | O que faz | Parâmetros |
|---|---|---|
| `listArticles` | Lista artigos paginados (status, datas, tag, autor, search). | status, dateFrom, dateTo, tagId, authorUserId, search, page, pageSize |
| `getArticle` | Detalhe do artigo; includeVirtual/includeContent opcionais. | publishNewsId (obrig.), includeVirtual, includeContent |
| `listTags` | Tags do portal (paginado). | page, pageSize, search |
| `getTag` | Detalhe de uma tag. | publishTagId (obrig.) |
| `listAuthors` | Autores ativos do portal. | page, pageSize |
| `proposeArticleDraft` | Valida JSON do editor sem gravar (novo ou existente). | publishNewsId (new ou id), articleJson (obrig.), authorUserId (obrig. em novos) |
| `applyArticleDraft` | Cria ou atualiza rascunho (status 0 ou virtual de publicado). | publishNewsId (new ou id), articleJson (obrig.), authorUserId (obrig. em novos) |
| `proposeArticleMeta` | Valida alteração de meta (título, capa, tag, SEO, autor) sem gravar. | publishNewsId (obrig.), title, subtitle, image, tagId, titleTag, titleSocial, authorUserId |
| `applyArticleMeta` | Aplica meta no artigo e sincroniza JSON virtual. | publishNewsId (obrig.), campos de meta incluindo authorUserId |
| `applyArticleStatus` | Retira o artigo do rascunho (status=1 no banco) e publica sitemap-news.xml. Não envia o HTML do artigo — depois use Notícias → Atualizar notícias no painel. Bloqueado em free-tier. | publishNewsId (obrig.), status (1) |
| `getNewsLayout` | Baixa layout de notícias (ext. 4) por type na última versão. Somente equipe Interago / administrador. | type (obrig.) |
| `listNewsLayoutVersions` | Lista versões históricas do layout de notícias por type. Somente equipe Interago / administrador. | type (obrig.) |
| `getNewsLayoutVersion` | Baixa versão específica do layout de notícias por type. Somente equipe Interago / administrador. | type (obrig.), templatechangesId ou build |
| `proposeNewsLayout` | Valida alteração de layout sem gravar; retorna erros e htmlPreview. Somente equipe Interago / administrador. | type, code (obrig.), previewId |
| `applyNewsLayout` | Salva layout de notícias após validação (malware + compile). Somente equipe Interago / administrador. | type, code (obrig.), previewId |

## `webstories`: Web Stories

Módulo webstories — rascunho, publicação e listagem (ext. 14). Imagens vêm do Media Center (listMedia). Publicar envia HTML à hospedagem. Layouts PHP continuam só no painel.

| Método | O que faz | Parâmetros |
|---|---|---|
| `listWebstories` | Lista web stories paginados (rascunho e/ou publicados). | status (0/1), search, page, pageSize |
| `getWebstory` | Detalhe de um web story, com páginas (JSON do editor). | webstoryId (obrig.), includePages |
| `getWebstoriesConfig` | Caminho público, host e URL da lista.html. | — |
| `proposeWebstory` | Valida capa e páginas sem gravar. webstoryId=new cria; ID atualiza. | webstoryId (new ou id), title, description, image, pages (JSON) |
| `applyWebstory` | Cria ou atualiza o web story no banco (não publica no site). | webstoryId (new ou id), title, description, image, pages (JSON) |
| `deleteWebstory` | Apaga apenas rascunho (status 0). Publicado retorna 409 WEBSTORY_PUBLISHED. | webstoryId (obrig.) |
| `applyWebstoryPublish` | Publica na hospedagem (lista.html + slug.html) e grava a URL pública. Exige caminho em Configurações e FTP/SFTP padrão. | webstoryId (obrig.) |
| `applyWebstoriesRefresh` | Republica lista.html (sem webstoryId) ou o HTML de um story já publicado. | webstoryId (opcional) |

## `pages`: Páginas e Blocos

Módulo pages — leitura de páginas/blocos, criação, alterações via propose/apply e CRUD de linhas da variante 23 (repetição).

| Método | O que faz | Parâmetros |
|---|---|---|
| `listPages` | Lista páginas da loja (paginado). | page, pageSize (máx. 50), search |
| `createPage` | Cria uma página (url normalizada e única por loja). | name (obrig.), url, comment |
| `getPage` | Metadados da página e blocos no layout atual. | pageId (obrig.) |
| `getPageDraft` | Rascunho atual ou por draftId, com draftCode e blocos parseados. | pageId (obrig.), draftId |
| `getPageBuild` | Última build publicada ou buildId específico. | pageId (obrig.), buildId |
| `listBlocks` | Lista blocos da loja (paginado). Traz editorAvailable/backendAvailable. | page, pageSize, search |
| `listBlockVariants` | Lista as variantes com editor no painel (válidas para createBlock/repairBlock). | — |
| `createBlock` | Cria um bloco em variante suportada (rejeita variantes sem editor). Legado #7 → #12. Variante 23 (repetição): envie content (HTML template); virtualContent é gerado pela API e enviado manualmente retorna 422 com o formato interno esperado. | name (obrig.), blockvariantId (obrig.; alias variantId), description, content. Não envie virtualContent. |
| `repairBlock` | Corrige um bloco preso em variante sem editor, reatribuindo variante suportada. Grava BlockSnapshot. | blockinwebsiteId (obrig.), blockvariantId (obrig.) |
| `getBlock` | Detalhe do bloco; includeContent=0 para omitir HTML. | blockinwebsiteId (obrig.), includeContent |
| `listPageBlocks` | Blocos de uma página na ordem das linhas. | pageId (obrig.) |
| `proposeBlockContent` | Valida alteração de bloco sem gravar. Envie content (HTML completo) OU operations (find/replace no HTML publicado) — nunca os dois. Em variante 23 (repetição), content redefine o template (gera 1 linha, fieldName vazio); operations só altera o HTML publicado e não cria itens nem nomeia campos. | blockinwebsiteId (obrig.), content OU operations (não ambos). Não envie virtualContent. |
| `applyBlockContent` | Aplica alteração validada; grava BlockSnapshot. Envie content (HTML completo) OU operations (find/replace no HTML publicado) — nunca os dois. Não envie virtualContent. Em variante 23 (repetição), content redefine o template (gera 1 linha, fieldName vazio — nomeie depois com updateBlockFieldNames); operations só altera o HTML publicado e não cria itens nem nomeia campos. Para gerenciar itens use listBlockLines / createBlockLine / updateBlockLine / updateBlockFieldNames / deleteBlockLine / reorderBlockLines. Não republica páginas. | blockinwebsiteId (obrig.), content OU operations (não ambos). Não envie virtualContent. |
| `listBlockLines` | Lista as linhas de um bloco de repetição (variante 23), paginado. Retorna lineCount (total) + a página em lines. Com includeHtml=1, formata lineHtml só da página. HTML final do bloco também vem em getBlock (includeContent=1). Não envie virtualContent. | blockinwebsiteId (obrig.), includeHtml (default 1), includeTemplate (default 0), page, pageSize (ou offset, limit) |
| `createBlockLine` | Insere linha(s) vazias no bloco de repetição (variante 23): clona a estrutura de originalLine (inclui fieldName) e zera os valores (não copia valores do template). position: start/end/before/after/index. Opcional fields para preencher na criação. Rate limit: 30 req/min e 200 linhas/min por loja (429 RATE_LIMITED). Não envie virtualContent. Não republica páginas. | blockinwebsiteId (obrig.), count, position, referenceLineId, index, fields (JSON), includeHtml (default 0) |
| `updateBlockFieldNames` | Organiza os campos da variante 23 como a tela do painel depois de compilar o HTML (saveDataFields). O value de cada campo (mín. 2 caracteres) vira fieldName, salvo se for um fieldId antigo: aí mantém nome e valor anteriores. lineName é o ID que nomeia as linhas (ex.: field-0). O nome não aceita sinal de menor, sinal de maior nem entidades que viram tag. Aspas literais, a entidade de aspas e entidades comuns (e comercial, acentos) permanecem texto. Se o bloco já tem um valor malicioso gravado, a chamada responde 422 BLOCK_INCOMPATIBLE: o HTML reconstruído continua recusado. Limpe esse valor com updateBlockLine ou apague a linha antes de renomear. Não envie virtualContent. Não republica páginas. createBlockLine seguinte herda os nomes. | blockinwebsiteId (obrig.), lineName (obrig.), fields (JSON obrig.) |
| `updateBlockLine` | Atualiza valores de campos de uma linha (variante 23) por fieldId. fieldName sem fieldId só localiza um nome já único. fieldId com fieldName igual ao atual é ignorado (pode reenviar os fields do listBlockLines). fieldId com fieldName diferente responde 422 FIELD_NAME_NOT_PERSISTED (não grava o rótulo). Valor com entidades que viram tag HTML responde 422. Esquema javascript, vbscript ou data em atributo de URL responde 422 mesmo com caractere de controle ou espaço no meio, com ou sem entidade. A entidade de aspas e entidades comuns permanecem texto. Para nomear o schema use updateBlockFieldNames. Não envie virtualContent. Não republica páginas. | blockinwebsiteId, lineId, fields (JSON obrig.), includeHtml (default 0) |
| `deleteBlockLine` | Remove uma linha do bloco de repetição (variante 23). Bloqueia a última linha (422 LINE_LAST_FORBIDDEN). Não envie virtualContent. Não republica páginas. | blockinwebsiteId, lineId, includeHtml (default 0) |
| `reorderBlockLines` | Reordena todas as linhas do bloco de repetição (variante 23). Envie lineIds com a ordem completa (permutação de todos os lineId). Não envie virtualContent. Não republica páginas. | blockinwebsiteId, lineIds (JSON array obrig.), includeHtml (default 0) |
| `proposePageDraft` | Valida rascunho HTML com tags iBlock sem gravar. | pageId, draftCode (obrig.) |
| `applyPageDraft` | Salva rascunho e atualiza BlockInPages. | pageId, draftCode (obrig.) |

## `media`: Mídias

Módulo media — lista arquivos do Media Center (CDN / tabela MediaAsset), a mesma fonte do iMedia no painel. Não faz upload nem sync.

| Método | O que faz | Parâmetros |
|---|---|---|
| `listMedia` | Lista mídias do Media Center. Cada arquivo retorna cdnUrl (cdn-app /img ou /file) e localUrl (cdn-app /file original, para SEO/favicon), ambos com a estrutura de pastas. Use search/recursive para achar por nome. | dir, search, filesOnly (0/1), recursive (0/1), page, pageSize |

## `seo`: SEO

Módulo seo — dados fixos e SEO por página (ext. 3). Configure os Dados Fixos (updateEssentials) antes de consultar ou gravar o SEO das páginas.

| Método | O que faz | Parâmetros |
|---|---|---|
| `getEssentials` | Retorna os dados fixos de SEO da loja e os pré-requisitos de cada schema. | — |
| `updateEssentials` | Cria ou atualiza os dados fixos (upsert). Atualização parcial: só os campos enviados mudam. | seoAuthor, seoOrganizationName, seoOrganizationPhone, seoBaseHref (obrig.), demais opcionais |
| `listPageSeo` | Lista o SEO das páginas, paginado de 50 em 50. Filtre por search e/ou pageIds (1 ou n páginas). | page, pageSize (máx. 50), search, pageIds |
| `getPageSeo` | SEO resolvido de uma página (valor salvo ou defaults dos dados fixos). | pageId (obrig.), includeCode |
| `applyPageSeo` | Insere ou atualiza (upsert) o SEO de uma página. Campos omitidos mantêm o valor atual. | pageId (obrig.), title, description, keywords, imageUrl, social, organization, article, store, includeCode |
