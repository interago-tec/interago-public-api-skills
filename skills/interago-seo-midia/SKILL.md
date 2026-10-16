---
name: interago-seo-midia
description: >-
  Ajusta o SEO de uma loja ou site Interago pela API (dados fixos da empresa,
  título, descrição, imagem social e schemas por página) e encontra imagens e
  arquivos no Media Center. Use quando a pessoa pedir para melhorar o Google,
  mudar título ou descrição de página, imagem de compartilhamento, ou achar o
  link de uma imagem.
---

# SEO e Media Center

Pré-requisito: `interago-api`. SEO precisa da extensão SEO (`SEO_EXTENSION_REQUIRED` se faltar).

## 1. Dados fixos primeiro

Os dados fixos (nome da empresa, telefone, endereço do site, logo) alimentam o SEO de todas as páginas. Sem eles, o SEO por página falha com `ESSENTIALS_REQUIRED`.

```bash
python3 scripts/interago_api.py loja seo getEssentials
python3 scripts/interago_api.py loja seo updateEssentials seoAuthor="Nome" seoOrganizationName="Empresa" seoOrganizationPhone="+55 11 0000-0000" seoBaseHref=https://www.dominio.com.br
```

- Obrigatórios: `seoAuthor`, `seoOrganizationName`, `seoOrganizationPhone`, `seoBaseHref`.
- Só os campos enviados mudam.
- URLs (`seoBaseHref`, `seoOrganizationUrl`, `seoOrganizationLogo`) precisam ser `https://` válidas.
- `getEssentials` traz `prerequisites`: o que falta para ligar cada schema.
- `seoBaseHref` é também o endereço da loja que você manda para a pessoa.

Use os dados reais que a pessoa der. Não invente telefone, endereço ou nome.

## 2. SEO por página

```bash
python3 scripts/interago_api.py loja seo listPageSeo page=1 pageSize=50
python3 scripts/interago_api.py loja seo getPageSeo pageId=ID
python3 scripts/interago_api.py loja seo applyPageSeo pageId=ID title="..." description="..." imageUrl=URL
```

- Campos omitidos mantêm o valor atual.
- `social`, `organization`, `article`, `store` (0/1) ligam schemas. Cada um exige dados fixos; se faltar, `422 TOGGLE_PREREQUISITE_MISSING` diz o quê.
- `applyPageSeo` grava sem propose. Mostre o título e a descrição antes e peça o OK.
- `includeCode=1` devolve o HTML gerado, para conferir.

Boas práticas:

| Campo | Regra |
|---|---|
| `title` | Até ~60 caracteres. O assunto da página primeiro, a marca no fim. Único por página. |
| `description` | Até ~155 caracteres. O que a pessoa encontra e um motivo para clicar. Sem repetir o título. |
| `imageUrl` | Imagem de compartilhamento (1200×630 é o formato comum). Use `localUrl` do Media Center. |

Copy: sem travessão como pausa; ponto ou vírgula.

**Publicar:** painel → **SEO → Atualizar** e publicar a página (**Páginas → Publicar → Menu → Atualizar → Atualizar e Subir**). Confira com o link da página, vendo o código-fonte ou uma prévia de compartilhamento.

## 3. Media Center

A API **lista** arquivos. Não faz upload. Para subir imagem, a pessoa usa **Mídias** no painel (ou no editor de páginas).

```bash
python3 scripts/interago_api.py loja media listMedia search=logo filesOnly=1 recursive=1
python3 scripts/interago_api.py loja media listMedia dir=banners page=1 pageSize=50
```

Cada arquivo traz dois endereços:

| Campo | Use em |
|---|---|
| `cdnUrl` | Blocos, páginas, catálogo, capas (otimizado) |
| `localUrl` | SEO, favicon, imagem social, dados fixos (o arquivo original) |

- Pastas não têm URL.
- Arquivo que só está no servidor e nunca passou pelo Media Center pode não aparecer.
- Na loja grátis, listar uma pasta (`dir` preenchido) é bloqueado e não existem pastas: use a raiz com `search`.

Toda imagem em HTML leva `alt` descritivo (decorativa: `alt=""`).

## 4. Se a API não deixar

| Situação | Caminho |
|---|---|
| `FREE_TIER_DENIED` | Entregue título e descrição prontos. Painel → SEO → editar a página → Salvar → SEO → Atualizar. |
| Extensão SEO não instalada | Instalar em Extensões. Na grátis, pede Upgrade. |
| Precisa subir imagem | Painel → Mídias → enviar. Depois `listMedia search=` para pegar o link. |

Sitemap, robots.txt e llms.txt se atualizam em **Menu → Atualizar**, nos cards próprios.
