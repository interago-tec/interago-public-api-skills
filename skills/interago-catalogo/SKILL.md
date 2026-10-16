---
name: interago-catalogo
description: >-
  Cadastra e atualiza produtos, categorias, preços, estoques, variações,
  +Campos e tags de uma loja virtual Interago pela API, e publica o catálogo
  com autorização. Use quando a pessoa pedir para cadastrar produto, mudar
  preço ou estoque, criar categoria, ajustar variação (cor, tamanho), ou
  quando um produto não aparece na loja.
---

# Catálogo

Pré-requisito: `interago-api`. Precisa da extensão Catálogo (`CATALOG_EXTENSION_REQUIRED` se faltar).

## 1. O que nunca esquecer

1. **Gravar não publica.** Produto, preço, estoque, categoria e variação só aparecem na loja depois de atualizar o catálogo. A exceção são as tags (a busca lê na hora).
2. **`applyCatalogRefresh` só com um sim explícito da pessoa.** Ele recompila a loja inteira. Junte tudo, peça o OK uma vez, chame uma vez, com `--autorizado`. Se voltar `REFRESH_PENDING`, já tem uma rodando: espere.
3. **No update de produto, campo omitido pode ser apagado.** `applyProduct` segue o contrato antigo: omitir `price` zera o preço; `title` é sempre obrigatório. Leia o produto antes e reenvie o que não deve mudar. As exceções são `categoryId` e `additionalCategoryIds`: omitidos, não mudam.
4. **Não invente produto**, preço, foto ou descrição. Só o que a pessoa deu.

## 2. Ler

```bash
python3 scripts/interago_api.py loja catalog listProducts search=camiseta page=1 pageSize=50
python3 scripts/interago_api.py loja catalog getProduct productId=ID includeStock=1 includeTags=1
python3 scripts/interago_api.py loja catalog listCategories page=1 pageSize=50
python3 scripts/interago_api.py loja catalog getCatalogConfig
```

`getProduct` devolve `publicUrl`, o link do produto na loja. Guarde para mandar à pessoa.

## 3. Produto simples

Cadastro:

```bash
python3 scripts/interago_api.py loja catalog proposeProduct productId=new title="Camiseta Linho Azul" price=129.90 sku=CAM-LIN-AZ categoryId=12 stockQty=10
python3 scripts/interago_api.py loja catalog applyProduct   productId=new title="Camiseta Linho Azul" price=129.90 sku=CAM-LIN-AZ categoryId=12 stockQty=10
```

Atualização: `getProduct` → monte o mesmo conjunto de campos com a mudança → `proposeProduct` → `applyProduct`.

- `additionalCategoryIds`: lista substitui as categorias secundárias; `[]` remove todas; omitir não mexe.
- A resposta de `applyProduct` traz o preço gravado, relido do banco. Confira.
- Na loja grátis há teto de produtos (`FREE_TIER_PRODUCT_LIMIT`).

Online ou offline: `proposeProductStatus` / `applyProductStatus` com `status=1` ou `0`.

## 4. Preço e estoque em lote

Até 100 itens por chamada. Gasta 2 chamadas em vez de 200.

```bash
python3 scripts/interago_api.py loja catalog proposeProductPrices identifyBy=sku items='[{"sku":"CAM-LIN-AZ","price":119.9},{"sku":"CAM-LIN-BR","price":119.9}]'
python3 scripts/interago_api.py loja catalog applyProductStocks  identifyBy=productId items='[{"productId":101,"stockQty":5}]'
```

- Produto com variação: preço e estoque da opção só pelo SKU dela.
- A resposta separa `updated`, `unchanged` e `errors`. Relate os erros, um por um.

Estoque de um produto simples: `applyProductStock productId= stockQty=`. Deixa de valer depois que o produto ganha variações.

## 5. Categorias

```bash
python3 scripts/interago_api.py loja catalog proposeCategory categoryId=new name="Linho" parentId=ID_DA_MAE
python3 scripts/interago_api.py loja catalog applyCategory   categoryId=new name="Linho" parentId=ID_DA_MAE
```

- Sem `parentId`, nasce embaixo da raiz. A raiz da loja não se altera.
- O link é sempre `/cat/slug`, gerado do nome. Mudar o nome depois não muda o link; para mudar, envie `url=/cat/novo` (se estiver livre).
- `visible=0` esconde do menu.
- Não há apagar pela API. Apagar categoria é no painel.

## 6. Variações (cor, tamanho)

```bash
python3 scripts/interago_api.py loja catalog getProductVariations productId=ID
python3 scripts/interago_api.py loja catalog proposeProductVariations productId=ID variations=@workspace/loja/variacoes-ID.json
```

```json
[
  { "name": "Tamanho", "options": [
    { "name": "P", "sku": "CAM-LIN-AZ-P", "price": 0, "stockQty": 3 },
    { "name": "M", "price": 0, "stockQty": 5 }
  ]}
]
```

- Só opções simples, de um nível. Se `getProductVariations` disser `hasNestedOptions=true` (combinações, como Cor × Tamanho), a API não altera: é no painel.
- `price` da opção é **adicional** ao preço do produto, não o preço final.
- SKU vazio é gerado (`SKU-DO-PRODUTO-slug`). SKU repetido é recusado.
- Não apaga opções que você omitir. Até 50 opções.
- Depois disso o produto passa a ter variação: estoque e preço só pelo lote, por SKU.

## 7. +Campos e tags

```bash
python3 scripts/interago_api.py loja catalog getProductFilters productId=ID
python3 scripts/interago_api.py loja catalog proposeProductFilters productId=ID filters='{"1117":"Algodão e linho"}'
python3 scripts/interago_api.py loja catalog proposeProductTags productId=ID tags='["linho","verão"]' mode=merge
```

- +Campos são campos extras criados pela loja (texto, texto rico, mídia, HTML). A chave é o ID do campo.
- Tags: `mode=replace` (padrão) troca todas; lista vazia apaga. `merge` acrescenta. Valem na hora, sem refresh.

## 8. Publicar e mostrar

1. Liste o que mudou.
2. Pergunte: "Posso atualizar o catálogo agora? Ele publica tudo que está salvo na loja."
3. Com o sim: `python3 scripts/interago_api.py loja catalog applyCatalogRefresh --autorizado`
4. Sem o sim, ou na loja grátis, ensine: **Extensões → Catálogo → aba Atualizar** (ou **Menu → Atualizar → Catálogo → Atualizar catálogo**). Uma vez. Esperar a mensagem final.
5. Link: `python3 scripts/links.py loja produto PRODUCT_ID` (ou `categoria`, `catalogo`). Janela anônima.

Não apareceu? Siga em `interago-suporte` o checklist "produto não aparece": online, estoque, categoria, refresh rodou, link certo.

## 9. Se a API não deixar

| Situação | Caminho |
|---|---|
| `FREE_TIER_DENIED` | Passe os dados prontos e ensine: Extensões → Catálogo → aba Catálogo → novo produto ou editar → Salvar → aba Atualizar. |
| `PRODUCT_HAS_NESTED_VARIATIONS` | Variações no painel, na edição do produto. |
| Apagar categoria ou produto | Painel. |
| Planilha, importação em massa | Painel (bloqueado na grátis). |

Layout das páginas do catálogo (vitrine, produto, busca): `interago-layouts`.
