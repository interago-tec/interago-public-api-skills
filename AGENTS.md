# Agente Interago

Este repositório ensina um agente a operar uma loja Interago pela API. A pessoa é dona da loja, não da plataforma.

Leia primeiro `.cursor/skills/interago-comecar/SKILL.md` e siga a regra `.cursor/rules/interago.mdc`.

Não peça token no chat. Credenciais ficam em `.env.sites`. Na loja grátis há 100 chamadas de cortesia por mês (`account.getUsage`, que não gasta cota). Recurso bloqueado pelo plano ou cota esgotada: pare e indique o Upgrade, o faturamento Interago ou o suporte. Não contorne.
