# Habilidades públicas da API Interago

Ensina um agente (Cursor, Claude Code, Codex ou outro que leia `AGENTS.md`) a operar uma loja Interago pela API. A pessoa é dona da loja. Ela não precisa ser da equipe do Interago.

## O que já fica configurado ao abrir esta pasta

- Regra sempre ativa: `.cursor/rules/interago.mdc`
- Primeira skill: `.cursor/skills/interago-comecar/SKILL.md` (conta, loja grátis, API, cota, suporte)
- Cliente: `scripts/interago_api.py`
- Credenciais de exemplo: `.env.sites.example` (o arquivo real `.env.sites` não entra no Git)

Abra a **raiz deste repositório** no agente, não um chat solto sem a pasta. O guia completo é um só (`.cursor/skills/interago-comecar/SKILL.md`). Cada ferramenta tem um arquivo de entrada que aponta para ele:

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

`getUsage` não gasta a cota.

## Loja grátis, faturamento e suporte

A loja grátis serve para começar. Ela tem teto de catálogo e de mídia, e não deixa criar ou publicar páginas, instalar extensão, usar planilha nem atualização pesada do catálogo. Detalhe: https://www.interago.com.br/site/ajuda/31126-loja-gratis-limites-e-por-que-o-plano-pano-vale-a-pena

A API, na loja grátis ou sem faturamento, tem **100 chamadas de cortesia por mês**. Ao passar disso a resposta é `API_QUOTA_EXCEEDED` até o dia 1º. Também há teto de **60 chamadas por minuto**. Estourar o minuto pode bloquear a API até a equipe do Interago desbloquear.

Para mais chamadas ou recursos avançados:

- faça o Upgrade ou cadastre o faturamento no painel (com faturamento, pacotes de 8.000 chamadas a R$ 50);
- ou fale com o suporte do Interago.

Preços e o canal de suporte estão em https://www.interago.com.br/site/planos-e-precos (suporte normal para clientes com mensalidade a partir de R$ 50).

O cliente desta pasta consulta a cota antes de cada chamada e não envia a próxima quando a cortesia acabou.

## Licença

MIT. Veja `LICENSE`.

---

# Public skills for the Interago API

Teaches an agent (Cursor, Claude Code, Codex, or anything that reads `AGENTS.md`) to operate an Interago store through the API. The person owns the store. They do not need to work at Interago.

## What is already configured when you open this folder

- Always-on rule: `.cursor/rules/interago.mdc`
- First skill: `.cursor/skills/interago-comecar/SKILL.md` (account, free store, API, quota, support)
- Client: `scripts/interago_api.py`
- Credential sample: `.env.sites.example` (the real `.env.sites` file is gitignored)

Open the **root of this repository** in the agent. A browser chat that never opens the folder sees none of this. There is one full guide (`.cursor/skills/interago-comecar/SKILL.md`). Each tool has an entry file that points at it:

| Tool | What it reads on its own |
|---|---|
| Cursor | `.cursor/rules/` and `.cursor/skills/` |
| Claude Code | `CLAUDE.md` (pulls in `AGENTS.md`) and `.claude/skills/` |
| Codex | `AGENTS.md` and `.agents/skills/` |
| GitHub Copilot | `.github/copilot-instructions.md` and `.github/skills/` |
| Kiro | `AGENTS.md`, `.kiro/steering/`, and `.kiro/skills/` |
| Gemini CLI | `GEMINI.md` |

Junie, Amp, Cline, and Devin also read the root `AGENTS.md`.

## First steps

1. Create the store at https://app.interago.com.br/ (wizard: name, postal code, brand). The free store does not ask for a card.
2. In the panel, open **API Interago**, note the `websiteId`, click **Gerar novo token**, turn on **API ativa**, and save. Guide: https://www.interago.com.br/site/ajuda/33178-api-como-habilitar
3. Copy `.env.sites.example` to `.env.sites` and fill in `alias=websiteId:token`. Do not paste the token into chat.
4. Check: `python3 scripts/interago_api.py alias account getUsage`

`getUsage` does not spend quota.

## Free store, billing, and support

The free store is the starting point. It caps the catalog and media library, and it blocks new pages, publishing, new extensions, spreadsheets, and a full catalog refresh. Details: https://www.interago.com.br/site/ajuda/31126-loja-gratis-limites-e-por-que-o-plano-pano-vale-a-pena

On the free store, or without Interago billing, the API includes **100 courtesy calls per month**. Past that, calls return `API_QUOTA_EXCEEDED` until the 1st. There is also a cap of **60 calls per minute**. Going past the per-minute cap can lock the store's API until the Interago team unlocks it.

For more calls or advanced features:

- upgrade the store or turn on Interago billing in the panel (with billing, packs of 8,000 calls at R$ 50);
- or contact Interago support.

Prices and the support channel are on https://www.interago.com.br/site/planos-e-precos (standard support for customers on a plan from R$ 50 per month).

The client in this folder checks the quota before each call and does not send the next one when the courtesy allowance is gone.

## License

MIT. See `LICENSE`.
