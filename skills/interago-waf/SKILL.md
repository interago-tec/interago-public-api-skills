---
name: interago-waf
description: >-
  Resolve o erro 403 PAYLOAD_REJECTED da API Interago, causado pelo filtro de
  segurança que recusa certos trechos em HTML, CSS e JS (crase de template
  literal, eval, exec, chaves duplas, PHP). Use quando proposeBlockContent,
  applyBlockContent, proposePageDraft, applyPageDraft ou um layout voltar
  PAYLOAD_REJECTED, ou antes de enviar JS para a API.
---

# PAYLOAD_REJECTED: o filtro de segurança

A API passa todo conteúdo por um filtro de segurança **antes** de gravar. Quando ele encontra um trecho suspeito, recusa a requisição inteira com `403 PAYLOAD_REJECTED`.

**Não é tamanho.** Não corte o HTML. Ache o trecho e reescreva.

## 1. O que o filtro recusa

| Trecho | Troque por |
|---|---|
| Crase de template literal: `` `texto ${x}` `` | Aspas e concatenação: `'texto ' + x` |
| `${…}` | Concatenação |
| `{{…}}` | Outro marcador, ou montar por JS sem chaves duplas |
| `eval(` | Remover. Use JSON.parse, funções nomeadas |
| `regex.exec(` | `texto.match(regex)` ou `regex.test(texto)` |
| `<?php` | Nada de PHP em página ou bloco |
| Palavras soltas como php, exec, shell, cmd em código | Renomear a variável ou o texto |

O cliente deste repositório (`scripts/interago_api.py`) procura esses trechos antes de enviar e para com a linha do problema. Também barra `//` dentro de `<script>`, que não é do filtro mas quebra o script no Interago.

## 2. Exemplos

```js
/* recusado */
var banner = `<iBlock name="BannerPrincipal" bw="1234" />`;
document.querySelector(`#lista .item[data-id="${id}"]`);

/* aceito */
var banner = '<iBlock name="BannerPrincipal" bw="1234" />';
document.querySelector('#lista .item[data-id="' + id + '"]');
```

## 3. Conteúdo igual ao do site e mesmo assim recusado

O painel pode ter salvo um trecho com crase. A API valida o que você **envia**, antes de comparar com o que está gravado. Então reenviar o bloco idêntico ao `getBlock` pode dar `PAYLOAD_REJECTED`.

`operations` também passa pelo filtro: se o `find` contém crase, falha.

**Ordem:** primeiro tire todas as crases e trechos da tabela do bloco inteiro → depois faça a sua mudança → `propose*` → `apply*`.

## 4. Segunda camada

Além dos padrões fixos, há uma análise automática de trechos de código. JS com cara de carregador remoto (requisição + `innerHTML` com HTML de fora), timers complexos ou ofuscação podem ser recusados mesmo sem nenhum item da tabela.

- Interação de interface (abas, carrossel, acordeão): prefira CSS (`:checked`, `<details>`).
- Carregar menu ou rodapé de outro arquivo: `fetch` + `DOMParser` + `appendChild`.
- Uma tentativa com o JS reescrito. Se recusar de novo, não insista: entregue o código em arquivo e ensine a pessoa a colar no painel (**Menu → Editar Blocos** → bloco → colar → Salvar; depois publicar, `interago-suporte`).

## 5. Outros códigos parecidos

| Código | O que é |
|---|---|
| `BLOCK_INCOMPATIBLE` | Bloco inválido ou acima de 40.000 caracteres. Aqui sim é tamanho. |
| `LAYOUT_PHP_TAG_NOT_ALLOWED`, `LAYOUT_MALWARE_BLOCKED` | Layout com PHP ou código perigoso. |
| `DRAFT_FORBIDDEN_CONTENT` | Rascunho de página com conteúdo proibido. Leia `errors`. |
