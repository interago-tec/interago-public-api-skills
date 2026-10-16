---
name: interago-pedidos-envios
description: >-
  Consulta pedidos e envia código de rastreio, cria e edita cupons, ajusta
  frete por faixa de CEP e medidas de produto, e lê os relatórios de uma loja
  Interago pela API. Use quando a pessoa perguntar de pedido, cliente,
  rastreio, cupom de desconto, frete, entrega própria ou vendas e visitas.
---

# Pedidos, cupons, frete e relatórios

Pré-requisito: `interago-api`.

**Dados de cliente são pessoais.** Mostre só o necessário para a tarefa. Não salve em arquivo do projeto nem cole em lugar público. Não mande CPF, endereço ou telefone completos sem a pessoa pedir.

## 1. Pedidos

```bash
python3 scripts/interago_api.py loja orders listOrders dateFrom=2026-10-01 dateTo=2026-10-15 page=1 pageSize=50
python3 scripts/interago_api.py loja orders getOrder orderId=ID
python3 scripts/interago_api.py loja orders listOrdersByDocument document=CPF_OU_CNPJ dateFrom=2026-01-01 dateTo=2026-10-15
```

- `dateFrom` e `dateTo` são obrigatórios. Pergunte o período se a pessoa não disse.
- Padrão: status 3 a 6 (pagos em diante).

**Rastreio:**

```bash
python3 scripts/interago_api.py loja orders addTrackingCodeToOrder orderId=ID trackingCode=CODIGO trackingUrl=URL
```

- Só para pedido elegível (status 3 a 5). Marca como Enviado (6). Grava direto: confirme o pedido e o código.
- Por documento em vez de `orderId`: se houver mais de um pedido elegível, volta `MULTIPLE_ELIGIBLE_ORDERS`; peça o número do pedido.

Pedido que não aparece ou pagamento que não confirma: checklist em `interago-suporte` (gateway, status).

## 2. Cupons

Precisa da extensão Cupons. Gravação bloqueada na loja grátis.

```bash
python3 scripts/interago_api.py loja coupons listCoupons status=active
python3 scripts/interago_api.py loja coupons checkCouponCode code=BEMVINDO10
python3 scripts/interago_api.py loja coupons createCoupon code=BEMVINDO10 discountType=percent discountValue=10 useLimit=100 useLimitPerPerson=1 startDate=2026-10-15 endDate=2026-11-15
python3 scripts/interago_api.py loja coupons updateCoupon couponId=ID endDate=2026-11-30
```

- Se a API recusar a data, confira o formato aceito no testador do painel (API Interago) para `createCoupon`.
- `discountType`: `percent` ou `value` (reais).
- Sem `code`, a API gera um de 6 caracteres.
- Sem `accountIds`, vale para a loja inteira.
- `code` não muda depois de criado.
- `createCoupon` e `updateCoupon` gravam direto. Mostre o resumo (desconto, validade, limites) e peça o OK.
- Cupom é oferta: o texto da promoção vai em HTML na página (título, parágrafo, link), não só numa imagem.

## 3. Frete

Precisa da extensão Envios. Gravação bloqueada na loja grátis.

**Entrega própria por faixa de CEP:**

```bash
python3 scripts/interago_api.py loja shipping listCepRanges
python3 scripts/interago_api.py loja shipping proposeCepRanges mode=append cepRanges=@workspace/loja/frete/faixas.json
python3 scripts/interago_api.py loja shipping applyCepRanges   mode=append cepRanges=@workspace/loja/frete/faixas.json
```

- `mode=replace` (padrão) **substitui todas** as faixas. `replace` com `[]` apaga tudo. Prefira `append` para acrescentar, e leia as faixas atuais antes.
- A ordem importa na cotação. O `propose` devolve a prévia ordenada.
- Vale na próxima cotação. Não precisa atualizar o catálogo.

**Medidas do produto para frete:**

```bash
python3 scripts/interago_api.py loja shipping getShippingDefaults
python3 scripts/interago_api.py loja shipping getProductMeasures productId=ID
python3 scripts/interago_api.py loja shipping applyProductMeasures productId=ID width=20 height=10 length=30 fragile=0
python3 scripts/interago_api.py loja shipping applyProductMeasuresBatch identifyBy=sku items='[{"sku":"CAM-LIN-AZ","width":20,"height":3,"length":30}]'
```

- Produto sem medidas usa as medidas padrão da loja.
- O peso fica no produto (`applyProduct`, em `interago-catalogo`).
- `deleteProductMeasures` volta o produto para o padrão.

Transportadoras, Correios, retirada e regras de frete grátis são configurados no painel, em **Envios**. Frete que não aparece no checkout: checklist em `interago-suporte`.

## 4. Relatórios

```bash
python3 scripts/interago_api.py loja visits listReports
python3 scripts/interago_api.py loja visits getReport report=NOME period=thisMonth
```

São os mesmos relatórios da tela Relatórios do painel. `listReports` diz quais existem nesta loja e os períodos aceitos. Resuma em poucas linhas, com números da resposta. Não estime.
