#!/usr/bin/env python3
"""Monta e confere os links públicos da loja, para mandar à pessoa.

    python3 scripts/links.py APELIDO                      endereço da loja
    python3 scripts/links.py APELIDO pagina PAGE_ID       link de uma página
    python3 scripts/links.py APELIDO produto PRODUCT_ID   link de um produto
    python3 scripts/links.py APELIDO catalogo             listagem do catálogo
    python3 scripts/links.py APELIDO categoria CATEGORY_ID

Cada link é aberto antes de ser mostrado. Só imprime "no ar" quando o site responde 200.
"Ainda não está no ar" quase sempre quer dizer que falta publicar ou atualizar no painel.
Gasta de 1 a 3 chamadas de API.
"""
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import interago_api as api  # noqa: E402


def chamar(site, module, method, **params):
    res = api.call(site[0], site[1], module, method, {k: str(v) for k, v in params.items()})
    return res if isinstance(res, dict) and res.get("status") == "success" else {}


def no_ar(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status == 200
    except (urllib.error.URLError, ValueError):
        return False


def base_da_loja(site):
    href = (chamar(site, "seo", "getEssentials").get("essentials") or {}).get("seoBaseHref") or ""
    if href.startswith("https://"):
        return href.rstrip("/")
    produtos = chamar(site, "catalog", "listProducts", page=1, pageSize=1).get("products") or []
    if produtos and produtos[0].get("publicUrl"):
        partes = urllib.parse.urlsplit(produtos[0]["publicUrl"])
        return partes.scheme + "://" + partes.netloc
    return ""


def caminho_catalogo(site):
    return ((chamar(site, "catalog", "getCatalogConfig").get("config") or {}).get("configPath") or "").strip("/")


def candidatos(base, tipo, alvo, site):
    if tipo == "pagina":
        pagina = chamar(site, "pages", "getPage", pageId=alvo).get("page") or {}
        url = (pagina.get("pageUrl") or "").strip("/")
        arquivo = (pagina.get("pageFile") or "").strip("/")
        if url in ("", "index") or arquivo in ("index.html", "index.php"):
            return [base + "/"]
        return [base + "/" + c for c in (url, arquivo, url + ".html") if c]
    if tipo == "produto":
        produto = chamar(site, "catalog", "getProduct", productId=alvo).get("product") or {}
        return [produto["publicUrl"]] if produto.get("publicUrl") else []
    if tipo == "catalogo":
        caminho = caminho_catalogo(site)
        return [base + "/" + caminho + "/" if caminho else base + "/"]
    if tipo == "categoria":
        categoria = chamar(site, "catalog", "getCategory", categoryId=alvo).get("category") or {}
        url = (categoria.get("categoryUrl") or categoria.get("url") or "").strip("/")
        caminho = caminho_catalogo(site)
        return [base + "/" + "/".join(p for p in (caminho, url) if p), base + "/" + url] if url else []
    return [base + "/"]


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    site = api.load_site(args[0])
    tipo = args[1] if len(args) > 1 else "loja"
    alvo = args[2] if len(args) > 2 else ""
    base = base_da_loja(site)
    if not base:
        sys.exit("Não achei o endereço da loja pela API. Peça para a pessoa abrir o painel e clicar em Ver loja.")
    vistos = []
    for url in candidatos(base, tipo, alvo, site):
        if url in vistos:
            continue
        vistos.append(url)
        if no_ar(url):
            print("no ar: " + url)
            return
    print("ainda não está no ar: " + (vistos[0] if vistos else base))
    print("Falta publicar ou atualizar no painel (Menu -> Atualizar), ou o endereço mudou. Veja a skill interago-suporte.")
    sys.exit(1)


if __name__ == "__main__":
    main()
