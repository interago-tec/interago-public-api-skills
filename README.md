# Habilidades públicas da API Interago

Ensina um agente (Cursor, Claude Code, Codex, Copilot, Kiro ou outro que leia `AGENTS.md`) a operar uma loja Interago pela API e a atender como o suporte do Interago: publicar, mostrar o resultado no site, resolver o que travou e indicar o caminho no painel. A pessoa é dona da loja. Ela não precisa ser da equipe do Interago.

## O que tem aqui

| Skill | Para quê |
|---|---|
| `skills/interago-comecar` | Conta, loja grátis, ligar a API, token, cota, faturamento |
| `skills/interago-suporte` | Salvar, Publicar e Atualizar; link da loja; "não aparece no site"; painel; quando chamar o suporte; índice da Central de Ajuda |
| `skills/interago-api` | Chamada, respostas, erros, propose/apply, limites, referência de métodos |
| `skills/interago-paginas-blocos` | Páginas, blocos, header, footer, listas repetidas |
| `skills/interago-catalogo` | Produtos, categorias, preço, estoque, variações, +Campos, tags |
| `skills/interago-layouts` | Layouts de catálogo e de notícias |
| `skills/interago-noticias` | Artigos e Web Stories |
| `skills/interago-seo-midia` | SEO e Media Center |
| `skills/interago-pedidos-envios` | Pedidos, rastreio, cupons, frete, relatórios |
| `skills/interago-html-padrao` | Grade, HTML semântico, CSS e JS no padrão da plataforma |
| `skills/interago-waf` | Erro `PAYLOAD_REJECTED` |

Scripts:

| Script | Faz |
|---|---|
| `scripts/interago_api.py` | Cliente da API. Lê a cota antes de cada chamada, barra conteúdo que a API recusa, exige `--autorizado` no refresh do catálogo |
| `scripts/links.py` | Acha o link da loja, de uma página, produto ou categoria, e confere se está no ar |
| `scripts/snapshot.py` | Cópia local da loja em `workspace/` (respeita a cota) |
| `scripts/sync_skills.py` | Espelha `skills/` nas pastas de cada ferramenta |
| `scripts/atualizar_ajuda.py` | Regera o índice da Central de Ajuda |
| `scripts/atualizar_metodos.py` | Regera a referência de métodos da API |

## Funciona em qualquer agente

Abra a **raiz deste repositório** no agente, não um chat solto sem a pasta. O conteúdo fica em `skills/`. Cada ferramenta tem um arquivo de entrada e uma cópia curta das skills que aponta para lá:

| Ferramenta | O que ela lê sozinha |
|---|---|
| Cursor | `.cursor/rules/` e `.cursor/skills/` |
| Claude Code | `CLAUDE.md` (puxa o `AGENTS.md`) e `.claude/skills/` |
| Codex | `AGENTS.md` e `.agents/skills/` |
| GitHub Copilot | `.github/copilot-instructions.md` e `.github/skills/` |
| Kiro | `AGENTS.md`, `.kiro/steering/` e `.kiro/skills/` |
| Gemini CLI | `GEMINI.md` |

Junie, Amp, Cline e Devin também leem `AGENTS.md` na raiz. Um chat no navegador que não abre esta pasta não vê nada disso.

## Primeiros passos

1. Crie a loja em https://app.interago.com.br/ (wizard: nome, CEP, marca). A loja grátis não pede cartão.
2. No painel, abra **API Interago**, anote o `websiteId`, clique em **Gerar novo token**, ligue **API ativa** e salve. Guia: https://www.interago.com.br/site/ajuda/33178-api-como-habilitar
3. Copie `.env.sites.example` para `.env.sites` e preencha `apelido=websiteId:token`. Não cole o token no chat.
4. Confira: `python3 scripts/interago_api.py apelido account getUsage`

`getUsage` não gasta a cota. Depois, peça ao agente o que precisa ("mude o preço deste produto", "meu produto não aparece", "me mande o link da loja").

## Gravar não é publicar

No Interago, salvar não coloca no ar. Produto e preço pedem atualizar o catálogo; página pede Publicar e depois Atualizar. O agente diz o que falta, ensina o caminho no painel e manda o link para conferir. Guia oficial: https://www.interago.com.br/site/ajuda/29716-mudo-x-atualizo-onde-manual-resumido-para-atualizar-a-loja-ou-site

## Loja grátis, faturamento e suporte

A loja grátis serve para começar. Ela tem teto de catálogo e de mídia, e não deixa criar ou publicar páginas, instalar extensão, usar planilha nem atualização pesada do catálogo. Detalhe: https://www.interago.com.br/site/ajuda/31126-loja-gratis-limites-e-por-que-o-plano-pano-vale-a-pena

**Pela API, a loja grátis lê e valida, mas não grava** páginas, blocos, catálogo, frete, cupons nem SEO (`FREE_TIER_DENIED`). Nela o agente prepara o conteúdo e ensina a aplicar pelo painel.

A API, na loja grátis ou sem faturamento, tem **100 chamadas de cortesia por mês**. Ao passar disso a resposta é `API_QUOTA_EXCEEDED` até o dia 1º. Também há teto de **60 chamadas por minuto**. Estourar o minuto pode bloquear a API até a equipe do Interago desbloquear.

Para gravar pela API, mais chamadas ou recursos avançados:

- faça o Upgrade ou cadastre o faturamento no painel (com faturamento, pacotes de 8.000 chamadas a R$ 50);
- ou fale com o suporte do Interago.

Preços e o canal de suporte estão em https://www.interago.com.br/site/planos-e-precos (suporte normal para clientes com mensalidade a partir de R$ 50).

## Manutenção

- Skill nova ou descrição mudada: edite `skills/<nome>/SKILL.md` e rode `python3 scripts/sync_skills.py`.
- Central de Ajuda mudou: `python3 scripts/atualizar_ajuda.py` (lê o site; leva alguns minutos).
- Métodos novos na API: `python3 scripts/atualizar_metodos.py`.

## Licença

MIT. Veja `LICENSE`.

---

# Public skills for the Interago API

Teaches an agent (Cursor, Claude Code, Codex, Copilot, Kiro, or anything that reads `AGENTS.md`) to operate an Interago store through the API and to help the way Interago support does: publish, show the result on the live site, fix what got stuck, and point to the right panel screen. The person owns the store. They do not need to work at Interago.

## What is here

| Skill | Purpose |
|---|---|
| `skills/interago-comecar` | Account, free store, enabling the API, token, quota, billing |
| `skills/interago-suporte` | Save, Publish, and Update; store links; "it doesn't show on the site"; the panel; when to call support; Help Center index |
| `skills/interago-api` | Calls, responses, errors, propose/apply, limits, method reference |
| `skills/interago-paginas-blocos` | Pages, blocks, header, footer, repeating lists |
| `skills/interago-catalogo` | Products, categories, price, stock, variations, custom fields, tags |
| `skills/interago-layouts` | Catalog and news layouts |
| `skills/interago-noticias` | Articles and Web Stories |
| `skills/interago-seo-midia` | SEO and the Media Center |
| `skills/interago-pedidos-envios` | Orders, tracking, coupons, shipping, reports |
| `skills/interago-html-padrao` | Grid, semantic HTML, CSS, and JS conventions |
| `skills/interago-waf` | The `PAYLOAD_REJECTED` error |

The skills are written in Portuguese, the language of the Interago panel and Help Center.

Scripts: `scripts/interago_api.py` (API client with quota check, content guard, and `--autorizado` for catalog refresh), `scripts/links.py` (finds and checks store, page, product, and category links), `scripts/snapshot.py` (local copy, quota-aware), `scripts/sync_skills.py`, `scripts/atualizar_ajuda.py`, `scripts/atualizar_metodos.py`.

## Works in any agent

Open the **root of this repository** in the agent. Content lives in `skills/`. Each tool has an entry file and short skill copies pointing there:

| Tool | What it reads on its own |
|---|---|
| Cursor | `.cursor/rules/` and `.cursor/skills/` |
| Claude Code | `CLAUDE.md` (pulls in `AGENTS.md`) and `.claude/skills/` |
| Codex | `AGENTS.md` and `.agents/skills/` |
| GitHub Copilot | `.github/copilot-instructions.md` and `.github/skills/` |
| Kiro | `AGENTS.md`, `.kiro/steering/`, and `.kiro/skills/` |
| Gemini CLI | `GEMINI.md` |

Junie, Amp, Cline, and Devin also read the root `AGENTS.md`. A browser chat that never opens the folder sees none of this.

## First steps

1. Create the store at https://app.interago.com.br/ (wizard: name, postal code, brand). The free store does not ask for a card.
2. In the panel, open **API Interago**, note the `websiteId`, click **Gerar novo token**, turn on **API ativa**, and save. Guide: https://www.interago.com.br/site/ajuda/33178-api-como-habilitar
3. Copy `.env.sites.example` to `.env.sites` and fill in `alias=websiteId:token`. Do not paste the token into chat.
4. Check: `python3 scripts/interago_api.py alias account getUsage`

`getUsage` does not spend quota.

## Saving is not publishing

In Interago, saving does not put a change live. Products and prices need a catalog update; pages need Publish and then Update. The agent says what is missing, walks the person through the panel, and sends the link to check.

## Free store, billing, and support

The free store is the starting point. It caps the catalog and media library, and it blocks new pages, publishing, new extensions, spreadsheets, and a full catalog refresh. Details: https://www.interago.com.br/site/ajuda/31126-loja-gratis-limites-e-por-que-o-plano-pano-vale-a-pena

**On the free store the API reads and validates but does not write** pages, blocks, catalog, shipping, coupons, or SEO (`FREE_TIER_DENIED`). The agent prepares the content and guides the person through the panel.

On the free store, or without Interago billing, the API includes **100 courtesy calls per month**. Past that, calls return `API_QUOTA_EXCEEDED` until the 1st. There is also a cap of **60 calls per minute**. Going past it can lock the store's API until the Interago team unlocks it.

To write through the API, get more calls, or unlock advanced features:

- upgrade the store or turn on Interago billing in the panel (with billing, packs of 8,000 calls at R$ 50);
- or contact Interago support.

Prices and the support channel are on https://www.interago.com.br/site/planos-e-precos (standard support for customers on a plan from R$ 50 per month).

## License

MIT. See `LICENSE`.
