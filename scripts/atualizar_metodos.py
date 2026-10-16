#!/usr/bin/env python3
"""Regera a referência de métodos a partir da lista oficial do painel.

    python3 scripts/atualizar_metodos.py

Fonte: https://app.interago.com.br/App/Api/panel/moduleMethods.js
Saída: skills/interago-api/referencia/metodos.md
"""
import html
import os
import re
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTE = "https://app.interago.com.br/App/Api/panel/moduleMethods.js"
DEST = os.path.join(ROOT, "skills", "interago-api", "referencia", "metodos.md")


def texto(valor):
    valor = html.unescape(valor.replace("\\'", "'"))
    valor = re.sub(r"<[^>]+>", "", valor)
    return re.sub(r"\s+", " ", valor).strip()


def main():
    req = urllib.request.Request(FONTE, headers={"User-Agent": "Mozilla/5.0"})
    js = urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace")
    modulos = list(re.finditer(r"^\s{4}([a-zA-Z0-9_]+):\s*\{\s*\n\s*title:\s*'([^']*)',\s*\n\s*module:\s*'([^']*)'", js, re.M))
    linhas = ["# Métodos da API Interago", "",
              "Gerado por `scripts/atualizar_metodos.py` a partir de " + FONTE + ".",
              "Se um método não estiver aqui, ele é mais novo que esta cópia: consulte a fonte.", ""]
    total = 0
    for i, mod in enumerate(modulos):
        trecho = js[mod.end(): modulos[i + 1].start() if i + 1 < len(modulos) else len(js)]
        intro = re.search(r"intro:\s*'((?:[^'\\]|\\.)*)'", trecho)
        linhas += ["## `" + mod.group(3) + "`: " + mod.group(2), ""]
        if intro:
            linhas += [texto(intro.group(1)), ""]
        linhas += ["| Método | O que faz | Parâmetros |", "|---|---|---|"]
        for bloco in re.split(r"\{\s*\n\s*name:\s*'", trecho)[1:]:
            nome = bloco.split("'", 1)[0]
            desc = re.search(r"desc:\s*'((?:[^'\\]|\\.)*)'", bloco)
            params = re.search(r"params:\s*'((?:[^'\\]|\\.)*)'", bloco)
            linhas.append("| `" + nome + "` | " + texto(desc.group(1) if desc else "").replace("|", "/") +
                          " | " + texto(params.group(1) if params else "").replace("|", "/") + " |")
            total += 1
        linhas.append("")
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, "w", encoding="utf-8") as fh:
        fh.write("\n".join(linhas))
    print(str(total) + " métodos em " + str(len(modulos)) + " módulos -> " + DEST)


if __name__ == "__main__":
    main()
