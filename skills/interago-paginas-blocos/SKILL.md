---
name: interago-paginas-blocos
description: >-
  Edita páginas e blocos de uma loja ou site Interago pela API: header, footer,
  banner, seções, CSS global, blocos de repetição, criar página ou bloco, e o
  rascunho da página com tags iBlock. Use quando a pessoa pedir para mudar
  texto, layout, cor, seção, cabeçalho, rodapé, menu ou criar uma página nova.
---

# Páginas e blocos

Pré-requisitos: `interago-api` (chamada e erros) e `interago-html-padrao` (como escrever o HTML).

## 1. Como uma página é montada

Uma página Interago é um **rascunho** (`draftCode`) que mistura HTML próprio com referências a **blocos**:

```html
<iBlock name="header" bw="1234"/>
<main>
  <h1>Sobre nós</h1>
  ...
</main>
<iBlock name="footer" bw="1240"/>
```

- `bw` é o `blockinwebsiteId` do bloco. O conteúdo do bloco vive no bloco, não na página.
- O mesmo bloco (header, footer, `customCSS`) aparece em várias páginas. Mudar o bloco muda todas.
- Cada `<iBlock .../>` fica em **uma linha só**.

| Quero mudar… | Onde |
|---|---|
| Cabeçalho, menu, rodapé, CSS global | O bloco (`applyBlockContent`) |
| Texto ou seção só desta página | O rascunho da página (`applyPageDraft`), ou o bloco da seção se ela for um bloco |
| Ordem das seções, incluir ou tirar um bloco | O rascunho da página |
| Item de lista repetida (cards, depoimentos, banners) | Linhas do bloco de repetição (seção 5) |

## 2. Achar o alvo

```bash
python3 scripts/interago_api.py loja pages listPages page=1 pageSize=50
python3 scripts/interago_api.py loja pages listPageBlocks pageId=PAGE_ID
python3 scripts/interago_api.py loja pages listBlocks search=header
python3 scripts/interago_api.py loja pages getBlock blockinwebsiteId=ID includeContent=0
```

Não varra todas as páginas para achar um bloco. `listBlocks search=` resolve.

Antes de mexer num `<iBlock>`, confirme com `getBlock` que o par `name` + `bw` existe nesta loja. Se o `bw` estiver errado (copiado de outra loja), troque pelo ID certo do bloco com o mesmo nome. Não apague a tag.

## 3. Editar um bloco

**Mudança pequena e conhecida:** `operations` (localizar e substituir). Gasta menos e não reenvia o bloco inteiro.

```bash
python3 scripts/interago_api.py loja pages proposeBlockContent blockinwebsiteId=ID \
  operations='[{"find":"Frete grátis acima de R$ 199","replace":"Frete grátis acima de R$ 149"}]'
```

`find` precisa existir igual no HTML atual (copie do `getBlock`). A resposta diz quantas operações aplicaram e quantas falharam. Se falhou, não grave.

**Mudança grande:** baixe, edite o arquivo, envie `content` com o bloco completo.

```bash
python3 scripts/interago_api.py loja pages getBlock blockinwebsiteId=ID includeContent=1 --out workspace/loja/blocos/ID.json
# edite workspace/loja/blocos/ID-header.html
python3 scripts/interago_api.py loja pages proposeBlockContent blockinwebsiteId=ID content=@workspace/loja/blocos/ID-header.html
python3 scripts/interago_api.py loja pages applyBlockContent blockinwebsiteId=ID content=@workspace/loja/blocos/ID-header.html
```

- `content` **ou** `operations`, nunca os dois.
- Nunca envie `virtualContent`.
- Teto de 40.000 caracteres por bloco (`BLOCK_INCOMPATIBLE`). Se passar, separe o CSS em outro bloco.
- `applyBlockContent` guarda a versão anterior (snapshot). No painel, o bloco tem histórico.

## 4. Editar o rascunho da página

```bash
python3 scripts/interago_api.py loja pages getPageDraft pageId=PAGE_ID --out workspace/loja/paginas/PAGE_ID.json
# edite workspace/loja/paginas/PAGE_ID-slug.html
python3 scripts/interago_api.py loja pages proposePageDraft pageId=PAGE_ID draftCode=@workspace/loja/paginas/PAGE_ID-slug.html
python3 scripts/interago_api.py loja pages applyPageDraft pageId=PAGE_ID draftCode=@workspace/loja/paginas/PAGE_ID-slug.html
```

- O parâmetro é `draftCode` (com `code` a API responde `DRAFT_REQUIRED`).
- Não cole o conteúdo dos blocos no rascunho. Só as tags `<iBlock>`.
- Não use `applyPageDraft` para mudar o HTML interno de um bloco.

## 5. Blocos de repetição (listas)

Blocos de repetição (variante 23) guardam itens em **linhas**: cada card, depoimento ou banner é uma linha com campos.

```bash
python3 scripts/interago_api.py loja pages listBlockLines blockinwebsiteId=ID
python3 scripts/interago_api.py loja pages updateBlockLine blockinwebsiteId=ID lineId=LINHA fields='[{"fieldId":"FIELD_ID","value":"Novo título"}]'
python3 scripts/interago_api.py loja pages createBlockLine blockinwebsiteId=ID count=1 position=end
python3 scripts/interago_api.py loja pages reorderBlockLines blockinwebsiteId=ID lineIds='[5,3,4]'
python3 scripts/interago_api.py loja pages deleteBlockLine blockinwebsiteId=ID lineId=LINHA
```

- Use os `fieldId` que o `listBlockLines` devolve.
- `reorderBlockLines` exige todos os `lineId`, sem faltar nenhum.
- A última linha não se apaga.
- Até 20 linhas por chamada, 100 no bloco.
- Para trocar o modelo (o HTML de cada item), `applyBlockContent` com `content`, e depois `updateBlockFieldNames` para nomear os campos.

## 6. Criar página ou bloco

```bash
python3 scripts/interago_api.py loja pages createPage name="Quem somos" url=quem-somos
python3 scripts/interago_api.py loja pages listBlockVariants
python3 scripts/interago_api.py loja pages createBlock name=bannerSobre blockvariantId=VARIANTE content=@arquivo.html
```

- Confira antes se já existe (`listPages search=`, `listBlocks search=`). Nome ou link repetido dá 409.
- `createPage` e `createBlock` gravam direto, sem propose. Confirme com a pessoa.
- Bloco preso em variante sem editor: `repairBlock` com uma variante de `listBlockVariants`.

## 7. Depois de gravar: publicar

**A API não publica páginas.** O que você gravou fica salvo, e o visitante só vê depois de:

1. Painel → **Meus websites** → a loja.
2. **Menu → Páginas** → abrir a página → **Salvar** → **Publicar**.
3. **Menu → Atualizar** → card **Páginas** → **Atualizar e Subir**.

Bloco usado em várias páginas (header, footer, `customCSS`): publique as páginas afetadas e use **Atualizar e Subir**. Se o bloco aparece também no catálogo, atualize o catálogo.

Mande o link: `python3 scripts/links.py loja pagina PAGE_ID`. Peça para abrir em janela anônima.

## 8. Se a API não deixar

| Situação | Caminho |
|---|---|
| `FREE_TIER_DENIED` | Entregue o HTML pronto em arquivo e ensine: Menu → Editar Blocos (ou Páginas → Blocos) → abrir o bloco → colar → Salvar. Criar e publicar página na grátis pede Upgrade. |
| `PAYLOAD_REJECTED` persistente | `interago-waf`. Se nada resolver, mesmo caminho do painel acima. |
| Precisa desfazer | Painel → editor da página → **Histórico** (restaurar versão), ou o histórico do bloco. |

Passo a passo completo do painel: `interago-suporte`.
