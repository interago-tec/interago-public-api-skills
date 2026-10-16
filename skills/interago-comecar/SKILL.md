---
name: interago-comecar
description: >-
  Prepara a pessoa e o agente para trabalhar no Interago: criar a conta, abrir
  a loja grátis, ligar a API, guardar o token fora do chat, conferir Python e
  a pasta do projeto, e respeitar a cota de 100 chamadas. Use no início de
  qualquer conversa, quando a pessoa acabou de baixar o repositório, quando
  pedir para configurar o Cursor, criar conta, ativar a API, ou quando a API
  responder API_QUOTA_EXCEEDED, loja grátis ou sem permissão.
---

# Começar no Interago

A pessoa que está com você é dona da própria loja. Ela não é da equipe do Interago e não administra a plataforma. O seu trabalho é deixá-la operando a loja com qualidade de webdesign, dentro do plano que ela tem.

Faça uma etapa por vez. Fale em português simples. Não peça senha nem token no chat.

## 1. O que este repositório já configura

Se a pasta deste repositório é a pasta aberta no Cursor, o agente já recebe:

- esta regra, em toda conversa (`.cursor/rules/interago.mdc`);
- esta skill e as skills de cada área (`.cursor/skills/`);
- o cliente da API (`scripts/interago_api.py`), que lê o token do arquivo, barra conteúdo que a API recusaria, não repete escrita com erro e para quando a cota de cortesia acaba;
- o exemplo de credenciais (`.env.sites.example`) e o `.gitignore`, que deixa `.env.sites` e `workspace/` fora do Git.

Se a pessoa usa este material dentro de outro projeto, copie a pasta `.cursor/` para a raiz desse projeto e copie também `scripts/`. Sem isso, o Cursor não carrega as skills.

Python 3 precisa existir (`python3 --version`). No Mac ele já vem. No Windows, oriente a instalar em python.org e marcar "Add python.exe to PATH".

## 2. Criar a conta e a loja grátis

Mande a pessoa para https://app.interago.com.br/

O wizard pede, nesta ordem: nome do projeto, CEP da operação, logo e cor da marca. A loja nasce gratuita para sempre, sem cartão e sem prazo de teste. O endereço inicial é no domínio do Interago (no formato `nome.interago.com.br`).

Diga, antes de ela avançar, o que a loja grátis é. Fonte: [Loja grátis: limites](https://www.interago.com.br/site/ajuda/31126-loja-gratis-limites-e-por-que-o-plano-pano-vale-a-pena).

Dá para colocar a loja no ar, cadastrar produtos até o teto do plano, usar o dia a dia e apontar o domínio da marca.

A loja grátis não deixa:

- criar, copiar, renomear, apagar ou publicar páginas pelo fluxo normal;
- instalar extensão nova;
- importar planilha nem disparar a atualização pesada do catálogo;
- usar os menus Contatos e Acesso (não convida outra pessoa para o painel);
- cadastrar telefone para relatório no WhatsApp;
- criar pastas de mídia (os arquivos ficam na gaveta principal, com teto de quantidade).

**Pela API, a loja grátis praticamente só lê e valida.** `get*`, `list*` e `propose*` funcionam. As gravações de páginas, blocos, catálogo (produto, preço, estoque, categoria, variação, refresh, layout), frete, cupons, SEO, publicação de notícia e pastas de mídia voltam `FREE_TIER_DENIED`, com o aviso "este recurso não está aberto para lojas grátis". Vale para qualquer token. Notícias e Web Stories dependem de extensões que a grátis não instala.

Então, na grátis, o seu papel é: ler a loja, preparar o conteúdo em arquivo, validar com `propose*` e ensinar a pessoa a aplicar pelo painel, passo a passo (skill `interago-suporte`). Para o agente gravar direto, a loja precisa do Upgrade.

Quando o painel ou a API recusar com o aviso de loja grátis, explique que é regra do plano, não um erro dela nem seu. O próximo passo é o painel, o Upgrade ou falar com o suporte. Não procure um jeito de contornar.

## 3. Ligar a API e guardar o token

Fonte: [API: como habilitar](https://www.interago.com.br/site/ajuda/33178-api-como-habilitar).

No painel da loja:

1. Abra o menu **API Interago** (tela Geral).
2. Anote o **websiteId** e o endpoint `https://app.interago.com.br/App/Api/index.php`.
3. Clique em **Gerar novo token**. Cada usuário tem o seu. Gerar de novo invalida o token anterior.
4. Ligue **API ativa**.
5. Clique em **Salvar**. Sem token, a API não liga.

Se o menu API Interago não aparecer, pare. Peça para ela falar com o suporte do Interago. Não invente outro endereço de API.

O token não entra no chat, nem em arquivo commitado, nem em print. Ela cria, na raiz do projeto, o arquivo `.env.sites` (pode copiar `.env.sites.example`):

```text
minhaloja=WEBSITE_ID:TOKEN
```

`minhaloja` é um apelido que vocês escolhem. Você só usa o apelido.

Se ela colar o token no chat mesmo assim, avise para gerar outro no painel (o colado deixa de valer) e seguir só com o arquivo.

## 4. Conferir o ambiente antes de editar

Rode, nesta ordem, e leia o resultado em voz alta para ela:

```bash
python3 --version
python3 scripts/interago_api.py minhaloja account getUsage
```

`getUsage` não gasta a cota do mês. Na resposta, olhe `usage`:

| Campo | Leitura |
|---|---|
| `billingModel: courtesy` | Cortesia. 100 chamadas no mês. Ao zerar, a API pausa. |
| `billingModel: packages` | Faturamento Interago ligado. Depois das 100, abre pacote de 8.000. |
| `remaining` | Quantas chamadas ainda cabem neste ciclo. |
| `resetsAt` | Quando o contador zera (cortesia: dia 1º do mês seguinte). |
| `pausesAtLimit: true` | Ao zerar, para. Não abre pacote sozinho. |
| `tokenCountsUsage: false` | Token da equipe Interago. Não é o caso desta pessoa. |

Se `getUsage` falhar com token ou API inativa, volte ao passo 3. Não tente outro método "para ver".

Uma leitura pequena, para provar que a loja responde:

```bash
python3 scripts/interago_api.py minhaloja pages listPages page=1 pageSize=1
```

Aí sim o ambiente está pronto.

## 5. Cota, faturamento e suporte

Há dois limites, e os dois importam.

**Por minuto:** 60 chamadas autenticadas por website. Estourar pode bloquear a API da loja. O desbloqueio é com a equipe do Interago, não com retry. O cliente espera sozinho só no 429 de leitura.

**Por mês:**

- Loja grátis ou sem faturamento: 100 chamadas de cortesia. Na 101 a resposta é `API_QUOTA_EXCEEDED` e a API fica pausada até o dia 1º. O cliente deste repositório para antes de enviar quando `remaining` chega a zero.
- Com faturamento Interago: depois das 100, pacotes de 8.000 chamadas (R$ 50 por pacote). O pacote seguinte abre sozinho e entra na fatura. Os detalhes ficam em Faturamento, no painel.

Preços públicos da plataforma (confira em [Planos e preços](https://www.interago.com.br/site/planos-e-precos), porque mudam):

- Upgrade da loja virtual a partir de R$ 90 por mês (até 100 produtos), subindo por faixa.
- Site institucional a partir de R$ 50 por mês.
- No Upgrade a primeira fatura entra no ciclo seguinte, não na hora.
- Suporte por WhatsApp e e-mail para clientes ativos com mensalidade a partir de R$ 50.

Quando ela pedir recurso que a grátis não tem, ou mais chamadas neste mês, diga as duas saídas, sem escolher por ela:

1. Cadastrar o faturamento ou fazer o Upgrade no painel (menu de planos / faturamento).
2. Falar com o suporte do Interago, pelo canal indicado em https://www.interago.com.br/site/planos-e-precos

Não prometa prazo, desconto nem que o suporte atende a loja grátis do mesmo jeito que a paga. O texto público reserva o suporte normal a quem tem mensalidade a partir de R$ 50.

## 6. Como gastar pouco e ainda trabalhar bem

Na cortesia, uma cópia da loja inteira (`scripts/snapshot.py`) pode acabar o mês. O script recusa a cópia completa quando restam menos de 12 chamadas e, acima disso, para sozinho 3 chamadas antes do zero.

Prefira o alvo mínimo:

- uma página (`getPageDraft`);
- um bloco (`getBlock`);
- um produto (`getProduct`).

`propose` + `apply` são duas chamadas. Conte antes. Para preço e estoque de vários produtos, use o método em lote (até 100 itens numa chamada), descrito na skill de catálogo.

Antes de uma leva, rode `getUsage` de novo. Se `remaining` não cobre a leva com folga de 3, pare e avise.

## 7. O que dá para fazer com qualidade, mesmo na grátis

Webdesign aqui é HTML semântico, grade `container` / `row` / `col-*`, CSS sem `!important`, texto no HTML (não só dentro de imagem) e conferir no navegador depois de gravar.

Na loja grátis, você entrega isso pronto e validado, e a pessoa cola no painel: o HTML do bloco, o texto do produto, o SEO da página. Use `propose*` para validar antes de entregar. Produtos ficam no teto do plano e a mídia na gaveta principal.

Não insista quando aparecer:

| Resposta | O que dizer a ela |
|---|---|
| `FREE_TIER_DENIED` | A API da loja grátis não grava. Passo a passo no painel (`interago-suporte`), ou Upgrade. |
| `FREE_TIER_PRODUCT_LIMIT` | Teto de produtos do plano. Upgrade. |
| Recusa de criar ou publicar página no painel | O plano não inclui. Upgrade ou suporte. |
| `API_QUOTA_EXCEEDED` | Cortesia do mês acabou. Faturamento, Upgrade, ou esperar o dia 1º. |
| `LAYOUT_STAFF_REQUIRED` | Este token não edita layout de catálogo nem de notícias. Isso pede administrador da loja ou a equipe do Interago. Não tente de novo. |
| `REFRESH_PENDING` | Já existe uma atualização rodando. Esperar. |
| API bloqueada por excesso por minuto | Pedir desbloqueio ao suporte do Interago. |

Gravar não publica o site. Catálogo no ar pede atualização (`applyCatalogRefresh`), e essa chamada só sai com um sim explícito dela, porque recompila a loja. Páginas se publicam no painel. Depois de qualquer gravação, diga o que falta publicar e mande o link para ela ver (`interago-suporte`).

## 8. Ordem das próximas skills

Ambiente conferido e cota lida. Aí sim:

| Tarefa | Skill |
|---|---|
| Publicar, ver no site, usar o painel, chamar o suporte, Central de Ajuda | `interago-suporte` |
| Entender chamada, erro e propose/apply | `interago-api` |
| Página, bloco, header, footer | `interago-paginas-blocos` |
| Produto, categoria, preço, estoque | `interago-catalogo` |
| Layout de catálogo ou notícias | `interago-layouts` |
| Notícias e Web Stories | `interago-noticias` |
| SEO e imagens | `interago-seo-midia` |
| Pedido, cupom, frete | `interago-pedidos-envios` |
| HTML e CSS no padrão da plataforma | `interago-html-padrao` |
| `PAYLOAD_REJECTED` | `interago-waf` |

Todos os métodos e parâmetros: `skills/interago-api/referencia/metodos.md`. Não invente o método. A lista oficial mora em https://app.interago.com.br/App/Api/panel/moduleMethods.js (leia só o método que falta) e no testador do painel, em API Interago.
