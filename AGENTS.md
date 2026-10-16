# Agente Interago

Este repositório ensina um agente a operar uma loja Interago pela API e a atender como o suporte do Interago. A pessoa é dona da loja, não da plataforma.

Leia primeiro `skills/interago-comecar/SKILL.md`. Depois, a skill da tarefa:

| Tarefa | Skill |
|---|---|
| Conta, loja grátis, ligar a API, cota, faturamento | `skills/interago-comecar/SKILL.md` |
| Publicar, ver no site, mandar o link, usar o painel, chamar o suporte, Central de Ajuda | `skills/interago-suporte/SKILL.md` |
| Chamada, erros, propose/apply, limites | `skills/interago-api/SKILL.md` |
| Página, bloco, header, footer | `skills/interago-paginas-blocos/SKILL.md` |
| Produto, categoria, preço, estoque, variação | `skills/interago-catalogo/SKILL.md` |
| Layout de catálogo ou notícias | `skills/interago-layouts/SKILL.md` |
| Notícias e Web Stories | `skills/interago-noticias/SKILL.md` |
| SEO e Media Center | `skills/interago-seo-midia/SKILL.md` |
| Pedidos, cupons, frete, relatórios | `skills/interago-pedidos-envios/SKILL.md` |
| HTML, CSS e JS no padrão | `skills/interago-html-padrao/SKILL.md` |
| `PAYLOAD_REJECTED` | `skills/interago-waf/SKILL.md` |

Regras que valem sempre:

- Não peça token no chat. Credenciais ficam em `.env.sites`.
- Na loja grátis há 100 chamadas de cortesia por mês (`account.getUsage`, que não gasta cota), e a API não grava páginas, blocos, catálogo, frete, cupons nem SEO (`FREE_TIER_DENIED`). Prepare o conteúdo e ensine pelo painel, ou indique o Upgrade, o faturamento Interago ou o suporte. Não contorne.
- `propose*` valida, `apply*` grava depois do OK da pessoa. Erro em gravação: releia antes de repetir.
- `applyCatalogRefresh` só com um sim explícito.
- Gravar não publica. Termine dizendo o que falta publicar e mandando o link (`python3 scripts/links.py`).
- Na dúvida sobre o painel, consulte a Central de Ajuda (`skills/interago-suporte/ajuda/README.md`).
