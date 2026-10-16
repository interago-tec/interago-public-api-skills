#!/usr/bin/env python3
"""Copia local de uma loja Interago: paginas, blocos, categorias, midia e (se permitido) layouts.

    python3 scripts/snapshot.py APELIDO [--sem-layouts]

So le. Nunca grava na loja. Saida em workspace/APELIDO/:
    paginas/<pageId>-<slug>.html       rascunho de cada pagina (com as tags <iBlock>)
    blocos/<blockinwebsiteId>-<nome>   conteudo de cada bloco (.html ou .json)
    catalogo/                          categorias e layouts (home, list, menu, product, data)
    midia/_index.json                  arquivos do Media Center

Respeita o limite de 60 chamadas por minuto da API (uma chamada a cada ~1,1 s).
"""
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import interago_api as api  # noqa: E402

PAUSA = 1.1
SLUG_RE = re.compile(r"[^a-z0-9]+")


def slug(text, fallback="item"):
    return SLUG_RE.sub("-", (text or "").lower()).strip("-") or fallback


def salvar(path, conteudo):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(conteudo if isinstance(conteudo, str) else json.dumps(conteudo, ensure_ascii=False, indent=2) + "\n")


class Loja:
    def __init__(self, alias):
        self.website_id, self.token = api.load_site(alias)
        self.teto = None
        self.feitas = 0

    def get(self, module, method, **params):
        if self.teto is not None and self.feitas >= self.teto:
            raise RuntimeError("parei para não zerar a cota de cortesia")
        self.feitas += 1
        time.sleep(PAUSA)
        res = api.call(self.website_id, self.token, module, method, {k: str(v) for k, v in params.items()})
        if not isinstance(res, dict) or res.get("status") != "success":
            raise RuntimeError(str((res or {}).get("code") or (res or {}).get("message") or res)[:200])
        return res

    def todos(self, module, method, chave, **params):
        itens, pagina = [], 1
        while pagina <= 40:
            res = self.get(module, method, page=pagina, pageSize=50, **params)
            lote = res.get(chave) or res.get("items") or []
            itens += lote
            if res.get("hasMore") is False or (res.get("hasMore") is None and len(lote) < 50):
                break
            pagina += 1
        return itens


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    alias = args[0]
    loja = Loja(alias)
    uso = api.quota_status(loja.website_id, loja.token) or {}
    if uso.get("pausesAtLimit"):
        resto = int(uso.get("remaining") or 0)
        if resto < 12:
            sys.exit("Copia completa gastaria a cota de cortesia (restam " + str(resto) + " chamadas). "
                     "Na loja grátis, peça um alvo só (uma página ou um bloco). "
                     "Para copiar a loja inteira, ative o faturamento Interago ou faça o Upgrade.")
        print("aviso: cortesia, restam " + str(resto) + " chamadas. A cópia para antes de zerar.")
        loja.teto = resto - 3
    base = os.path.join(os.getcwd(), "workspace", alias)
    print("Loja " + alias + " (" + loja.website_id + ") -> " + base)

    if "--sem-layouts" not in sys.argv:
        try:
            salvar(os.path.join(base, "catalogo", "engine.json"), loja.get("catalog", "getCatalogLayoutEngine"))
            for tipo in ("home", "list", "menu", "product", "data"):
                lay = loja.get("catalog", "getCatalogLayout", type=tipo)
                salvar(os.path.join(base, "catalogo", "layout-" + tipo + ".html"), lay.get("code") or "")
            print("  layouts ok")
        except RuntimeError as err:
            print("  layouts ignorados (" + str(err) + "). Leitura de layout exige equipe Interago ou administrador.")

    paginas = loja.todos("pages", "listPages", "pages")
    salvar(os.path.join(base, "paginas", "_index.json"), paginas)
    for p in paginas:
        pid = p.get("pageId")
        try:
            draft = loja.get("pages", "getPageDraft", pageId=pid)
            salvar(os.path.join(base, "paginas", str(pid) + "-" + slug(p.get("url") or p.get("name")) + ".html"),
                   draft.get("draftCode") or "")
        except RuntimeError as err:
            print("  pagina " + str(pid) + " falhou: " + str(err))
    print("  paginas: " + str(len(paginas)))

    blocos = loja.todos("pages", "listBlocks", "blocks")
    salvar(os.path.join(base, "blocos", "_index.json"), blocos)
    for b in blocos:
        bid = b.get("blockinwebsiteId")
        try:
            res = loja.get("pages", "getBlock", blockinwebsiteId=bid, includeContent=1)
            bloco = res.get("block") if isinstance(res.get("block"), dict) else res
            conteudo = bloco.get("content") or ""
            ext = ".json" if isinstance(conteudo, str) and conteudo.strip().startswith(("[", "{")) else ".html"
            salvar(os.path.join(base, "blocos", str(bid) + "-" + slug(b.get("blockName")) + ext), conteudo)
        except RuntimeError as err:
            print("  bloco " + str(bid) + " falhou: " + str(err))
    print("  blocos: " + str(len(blocos)))

    try:
        salvar(os.path.join(base, "catalogo", "categorias.json"), loja.todos("catalog", "listCategories", "categories"))
        salvar(os.path.join(base, "midia", "_index.json"), loja.todos("media", "listMedia", "items", recursive=1))
        print("  categorias e midia ok")
    except RuntimeError as err:
        print("  categorias/midia falhou: " + str(err))
    print("Pronto. Edite os arquivos em workspace/" + alias + "/ e envie com propose* -> apply*.")


if __name__ == "__main__":
    main()
