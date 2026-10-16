#!/usr/bin/env python3
"""Cliente de linha de comando para a API do Interago, com travas de seguranca.

    python3 scripts/interago_api.py APELIDO MODULO METODO [chave=valor ...] [chave=@arquivo] [--out arquivo.json]

Exemplos:
    python3 scripts/interago_api.py minhaloja catalog listProducts page=1 pageSize=50 --out workspace/minhaloja/api/produtos-1.json
    python3 scripts/interago_api.py minhaloja pages getBlock blockinwebsiteId=123 includeContent=1 --out workspace/minhaloja/blocos/123.json
    python3 scripts/interago_api.py minhaloja pages proposeBlockContent blockinwebsiteId=123 content=@workspace/minhaloja/blocos/123-header.html

Credenciais (nunca no chat, nunca no git), em um arquivo .env.sites:
    minhaloja=WEBSITE_ID:TOKEN
O arquivo e procurado em: $INTERAGO_SITES_FILE, ./.env.sites (pasta atual) e na raiz deste repositorio.

Travas:
- applyCatalogRefresh exige --autorizado (o humano precisa ter dito "pode atualizar a loja").
- Conteudo enviado (content, draftCode, code, articleJson, fields, operations) passa antes por um filtro
  local com os padroes que o filtro da API recusa (crase, eval(, .exec(, ${, <?php) e pelo erro classico
  de render (// dentro de <script>). Se falhar, nada e enviado. {{ gera so aviso.
- Metodos de escrita (apply*, create*, update*, delete*, reorder*, repair*) nunca sao repetidos
  automaticamente. Em erro, confira o estado com um get* antes de tentar de novo.
- Respostas grandes vao para --out; no terminal sai so um resumo.
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = os.environ.get("INTERAGO_BASE_URL", "https://app.interago.com.br/App/Api/index.php")
WRITE_PREFIXES = ("apply", "create", "update", "delete", "reorder", "repair")
CONTENT_KEYS = ("content", "draftCode", "code", "articleJson", "fields", "operations")
WAF_PATTERNS = [
    (re.compile(r"`"), "crase (template literal)"),
    (re.compile(r"\beval\s*\("), "eval("),
    (re.compile(r"\.exec\s*\("), ".exec("),
    (re.compile(r"\$\{"), "${"),
    (re.compile(r"<\?php", re.I), "<?php"),
]
WAF_WARNINGS = [
    (re.compile(r"\{\{"), "{{ (se a API responder PAYLOAD_REJECTED, este e o motivo provavel)"),
]
SCRIPT_RE = re.compile(r"<script\b(?![^>]*ld\+json)[^>]*>(.*?)</script>", re.S | re.I)


def sites_file():
    for path in (os.environ.get("INTERAGO_SITES_FILE", ""), os.path.join(os.getcwd(), ".env.sites"),
                 os.path.join(ROOT, ".env.sites")):
        if path and os.path.exists(path):
            return path
    sys.exit("Arquivo .env.sites nao encontrado. Crie na pasta do projeto com uma linha: apelido=websiteId:token")


def load_site(alias):
    with open(sites_file(), encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line.startswith(alias + "="):
                website_id, token = line.split("=", 1)[1].split(":", 1)
                return website_id.strip(), token.strip()
    sys.exit("Apelido '" + alias + "' nao encontrado em .env.sites")


def check_payload(value):
    """Lista o que o filtro da API recusaria neste conteudo. Lista vazia = pode enviar."""
    problems = []
    for pattern, label in WAF_PATTERNS:
        if pattern.search(value):
            problems.append(label)
    for pattern, label in WAF_WARNINGS:
        if pattern.search(value):
            print("aviso: contem " + label, file=sys.stderr)
    for block in SCRIPT_RE.findall(value):
        if re.search(r"(?<![:\"'])//", block) or "http://" in block or "https://" in block:
            problems.append("// dentro de <script> (use /* */ e monte URLs com String.fromCharCode(47))")
            break
    return problems


def call(website_id, token, module, method, params=None, retries=None):
    """Faz uma chamada e devolve o JSON. Leitura tenta ate 3 vezes; escrita, uma so."""
    body = {"websiteId": website_id, "module": module, "method": method}
    body.update(params or {})
    data = urllib.parse.urlencode(body).encode("utf-8")
    is_write = method.startswith(WRITE_PREFIXES)
    attempts = 1 if is_write else (retries or 3)
    result = None
    for attempt in range(attempts):
        req = urllib.request.Request(BASE_URL, data=data, headers={"Authorization": "Bearer " + token})
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw.strip() else {"status": "empty", "code": "EMPTY_BODY"}
        except urllib.error.HTTPError as err:
            raw = err.read().decode("utf-8", "replace")
            try:
                result = json.loads(raw)
            except json.JSONDecodeError:
                result = {"status": "error", "raw": raw[:400]}
            result.setdefault("http", err.code)
            if err.code == 429 and not is_write and attempt < attempts - 1:
                wait_for = int(result.get("retryAfterSeconds", 60))
                print("limite de chamadas, aguardando " + str(wait_for) + "s", file=sys.stderr)
                time.sleep(wait_for + 1)
                continue
            return result
        except urllib.error.URLError as err:
            result = {"status": "error", "code": "TRANSPORT", "detail": str(err)}
            if attempt < attempts - 1:
                time.sleep(3 * (attempt + 1))
                continue
    return result


def parse_args(argv):
    out, authorized, params, rest = None, False, {}, []
    i = 0
    while i < len(argv):
        if argv[i] == "--out":
            out = argv[i + 1]
            i += 2
            continue
        if argv[i] == "--autorizado":
            authorized = True
        else:
            rest.append(argv[i])
        i += 1
    if len(rest) < 3:
        sys.exit(__doc__)
    for pair in rest[3:]:
        if "=" not in pair:
            sys.exit("Parametro invalido: " + pair + " (use chave=valor)")
        key, value = pair.split("=", 1)
        if value.startswith("@"):
            with open(value[1:], encoding="utf-8") as fh:
                value = fh.read()
        params[key] = value
    return rest[0], rest[1], rest[2], params, out, authorized


def quota_status(website_id, token):
    """Lê account.getUsage. Essa chamada não consome a cota do mês.
    Devolve o dict usage, ou None se a leitura falhar."""
    info = call(website_id, token, "account", "getUsage", retries=1)
    if not isinstance(info, dict) or info.get("status") != "success":
        print("aviso: nao foi possivel ler a cota (account.getUsage). Siga com poucas chamadas.", file=sys.stderr)
        return None
    return info.get("usage") or {}


def quota_block(usage):
    """Mensagem de parada quando a cortesia do mês acabou. None se pode seguir."""
    if not usage or not usage.get("pausesAtLimit"):
        return None
    remaining = usage.get("remaining")
    if remaining is None or int(remaining) >= 1:
        if remaining is not None and int(remaining) <= 5:
            print("aviso: restam " + str(remaining) + " chamadas de cortesia neste mês.", file=sys.stderr)
        return None
    return ("COTA MENSAL ESGOTADA. Loja grátis ou sem faturamento Interago tem 100 chamadas de cortesia por mês. "
            "A API pausa até " + str(usage.get("resetsAt") or "o dia 1 do mês seguinte") + ". "
            "Para continuar antes: faça o Upgrade da loja ou ative o faturamento Interago no painel. "
            "Recursos avançados e desbloqueio: suporte do Interago (clientes com mensalidade).")


def summarize(data):
    if not isinstance(data, dict):
        return str(data)[:400]
    keep = {}
    for key, value in data.items():
        if isinstance(value, (list, dict)):
            keep[key] = "<" + type(value).__name__ + " com " + str(len(value)) + " itens>"
        elif isinstance(value, str) and len(value) > 300:
            keep[key] = value[:300] + "... (" + str(len(value)) + " caracteres)"
        else:
            keep[key] = value
    return json.dumps(keep, ensure_ascii=False, indent=2)


def main():
    alias, module, method, params, out, authorized = parse_args(sys.argv[1:])
    if method == "applyCatalogRefresh" and not authorized:
        sys.exit("BLOQUEADO: applyCatalogRefresh so com autorizacao explicita do humano. "
                 "Pergunte antes e, com o OK, rode de novo com --autorizado.")
    for key in CONTENT_KEYS:
        if key in params:
            problems = check_payload(params[key])
            if problems:
                sys.exit("BLOQUEADO antes de enviar (" + key + "): " + ", ".join(sorted(set(problems))) +
                         ". Corrija o conteudo e rode de novo. Nao encurte o conteudo.")

    website_id, token = load_site(alias)
    if not (module == "account" and method == "getUsage"):
        blocked = quota_block(quota_status(website_id, token))
        if blocked:
            sys.exit(blocked)
    result = call(website_id, token, module, method, params)
    code = result.get("code") if isinstance(result, dict) else None
    if code == "API_QUOTA_EXCEEDED":
        print("\nCOTA MENSAL ESGOTADA. Upgrade da loja ou faturamento Interago para continuar neste mês. "
              "Ou espere o dia 1. Link de upgrade: " + str(result.get("upgradeUrl") or "painel da loja"), file=sys.stderr)
    elif code in ("FREE_TIER_DENIED", "FREE_TIER_PRODUCT_LIMIT"):
        print("\nLOJA GRÁTIS: a API lê e valida (get, list, propose), mas não grava páginas, blocos, "
              "catálogo, frete, cupons nem SEO. "
              "Faça a alteração pelo painel (skill interago-suporte) ou faça o Upgrade.", file=sys.stderr)
    elif code == "API_BLOCKED":
        print("\nAPI BLOQUEADA nesta loja. Só a equipe do Interago desbloqueia. Não tente de novo.", file=sys.stderr)

    if out:
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(result, fh, ensure_ascii=False, indent=2)
        print("Resposta salva em " + out)
    print(summarize(result))

    failed = not isinstance(result, dict) or result.get("status") != "success"
    if failed and method.startswith(WRITE_PREFIXES):
        print("\nATENCAO: escrita com erro. Nao repita agora. Confira o estado com um get* "
              "(ou no painel) e so reaplique se a mudanca nao tiver entrado.", file=sys.stderr)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
