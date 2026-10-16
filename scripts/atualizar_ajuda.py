#!/usr/bin/env python3
"""Regera o índice da Central de Ajuda do Interago dentro da skill interago-suporte.

    python3 scripts/atualizar_ajuda.py            percorre https://www.interago.com.br/site/ajuda
    python3 scripts/atualizar_ajuda.py --cache DIR  usa uma coleta anterior (DIR/_meta.json + DIR/<slug>.txt)

Saída: skills/interago-suporte/ajuda/<tema>.md (título, resumo e link de cada artigo) e ajuda/README.md.
O índice não copia o texto dos artigos. O agente abre o link quando precisa do passo a passo atual.
"""
import html
import json
import os
import re
import sys
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, "skills", "interago-suporte", "ajuda")
SITE = "https://www.interago.com.br/site/"
TAGS = ("api", "arquivos", "artigos", "atualizacoes", "checkout", "conta", "envios", "ia", "institucional",
        "integracoes", "layout", "produtos", "promocoes", "relatorios", "updates")
HOME_TITLE = "Plataforma para Site, Loja Virtual e Portal de Notícia"
ARQUIVOS = {
    "Atualizações": "publicar-e-atualizar", "Updates": "novidades", "Conta": "conta-e-painel",
    "Layout": "paginas-e-layout", "Arquivos": "midias", "IA": "ia", "Institucional": "institucional",
    "Cadastro de Produtos": "produtos", "Produtos": "produtos", "Promoções": "promocoes",
    "Checkout": "checkout-e-pagamentos", "Configuração de Checkout": "checkout-e-pagamentos",
    "Envios": "envios-e-frete", "Integrações": "integracoes", "Relatórios": "relatorios",
    "Notícias e Blog": "noticias-e-blog", "API": "api",
}
TITULOS = {
    "publicar-e-atualizar": "Salvar, publicar e atualizar", "novidades": "Novidades da plataforma",
    "conta-e-painel": "Conta, painel, acesso e financeiro", "paginas-e-layout": "Páginas, blocos, layout e domínio",
    "midias": "Mídias e arquivos", "ia": "IA no painel", "institucional": "Institucional e páginas legais",
    "produtos": "Produtos e catálogo", "promocoes": "Promoções e cupons",
    "checkout-e-pagamentos": "Checkout, pedidos e pagamentos", "envios-e-frete": "Envios e frete",
    "integracoes": "Integrações, ERP e marketplaces", "relatorios": "Relatórios e visitas",
    "noticias-e-blog": "Notícias, blog e Web Stories", "api": "API", "outros": "Outros",
}


def baixar(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace")


def slugs(texto):
    return set(re.findall(r"ajuda/(\d+[-\w]*)", texto))


def ler_artigo(slug):
    try:
        pagina = baixar(SITE + "ajuda/" + slug)
    except Exception:
        return slug, None, set()
    titulo = re.search(r"<title>(.*?)</title>", pagina, re.S)
    resumo = re.search(r'<meta name="description" content="([^"]*)"', pagina)
    corpo = re.search(r"<article\b.*?</article>", pagina, re.S) or re.search(r"<main\b.*?</main>", pagina, re.S)
    texto = re.sub(r"<(script|style)\b.*?</\1>", "", corpo.group(0) if corpo else "", flags=re.S)
    texto = html.unescape(re.sub(r"<[^>]+>", "\n", texto))
    linhas = [l.strip() for l in texto.split("\n") if l.strip()]
    tema = linhas[2] if len(linhas) > 2 and linhas[1] == "Ajuda" else ""
    dados = {"title": html.unescape(titulo.group(1).strip()) if titulo else "",
             "desc": html.unescape(resumo.group(1)) if resumo else "", "cat": tema}
    return slug, dados, slugs(pagina)


def coletar():
    fila = slugs(baixar(SITE + "ajuda"))
    for tag in TAGS:
        try:
            fila |= slugs(baixar(SITE + "ajuda/tag/" + tag))
        except Exception:
            pass
    vistos, meta = set(), {}
    while fila:
        lote = list(fila - vistos)
        fila = set()
        with ThreadPoolExecutor(4) as pool:
            for slug, dados, novos in pool.map(ler_artigo, lote):
                vistos.add(slug)
                if dados:
                    meta[slug] = dados
                    fila |= novos
        fila -= vistos
    return meta


def da_cache(pasta):
    meta = json.load(open(os.path.join(pasta, "_meta.json"), encoding="utf-8"))
    for slug, dados in meta.items():
        caminho = os.path.join(pasta, slug + ".txt")
        if "cat" not in dados and os.path.exists(caminho):
            linhas = [l.strip() for l in open(caminho, encoding="utf-8").read().split("\n")[:6] if l.strip()]
            dados["cat"] = linhas[2] if len(linhas) > 2 and linhas[1] == "Ajuda" else ""
    return meta


def limpar(meta):
    por_id = {}
    for slug, dados in meta.items():
        if "error" in dados or not dados.get("title") or dados["title"].startswith(HOME_TITLE):
            continue
        numero = slug.split("-", 1)[0]
        atual = por_id.get(numero)
        if atual is None or (dados.get("cat") and not atual[1].get("cat")) or len(slug) > len(atual[0]):
            por_id[numero] = (slug, dados)
    return por_id.values()


def escrever(artigos):
    grupos = defaultdict(list)
    for slug, dados in artigos:
        grupos[ARQUIVOS.get(dados.get("cat", ""), "outros")].append((slug, dados))
    os.makedirs(DEST, exist_ok=True)
    for antigo in os.listdir(DEST):
        if antigo.endswith(".md"):
            os.remove(os.path.join(DEST, antigo))
    total = 0
    linhas_readme = []
    for arquivo in sorted(grupos, key=lambda a: list(TITULOS).index(a)):
        itens = sorted(grupos[arquivo], key=lambda x: x[1]["title"].lower())
        total += len(itens)
        corpo = ["# " + TITULOS[arquivo], "",
                 "Índice da Central de Ajuda do Interago. Abra o link para ler o passo a passo atual.", ""]
        for slug, dados in itens:
            titulo = re.sub(r"\s+", " ", dados["title"]).strip()
            resumo = re.sub(r"\s+", " ", dados.get("desc", "")).strip()
            corpo.append("- [" + titulo + "](" + SITE + "ajuda/" + slug + ")" + (". " + resumo if resumo else ""))
        with open(os.path.join(DEST, arquivo + ".md"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(corpo) + "\n")
        linhas_readme.append("| [" + TITULOS[arquivo] + "](" + arquivo + ".md) | " + str(len(itens)) + " |")
    readme = ["# Central de Ajuda do Interago: índice", "",
              "Gerado por `scripts/atualizar_ajuda.py` a partir de " + SITE + "ajuda (" + str(total) + " artigos).",
              "", "Busca ao vivo: " + SITE + "ajuda/assunto/q.html?m=search&q=PALAVRA", "",
              "| Tema | Artigos |", "|---|---|"] + linhas_readme
    with open(os.path.join(DEST, "README.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(readme) + "\n")
    print(str(total) + " artigos em " + str(len(grupos)) + " temas -> " + DEST)


def main():
    if "--cache" in sys.argv:
        meta = da_cache(sys.argv[sys.argv.index("--cache") + 1])
    else:
        meta = coletar()
    escrever(limpar(meta))


if __name__ == "__main__":
    main()
