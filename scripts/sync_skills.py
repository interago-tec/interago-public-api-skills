#!/usr/bin/env python3
"""Espelha skills/ nas pastas que cada agente lê sozinho.

    python3 scripts/sync_skills.py

A fonte única é skills/<nome>/SKILL.md. Para cada ferramenta, grava um SKILL.md curto com o mesmo
nome e descrição, apontando para a fonte. Rode depois de criar, renomear ou mudar a descrição de uma skill.
"""
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTE = os.path.join(ROOT, "skills")
DESTINOS = (".cursor/skills", ".claude/skills", ".agents/skills", ".github/skills", ".kiro/skills")


def frontmatter(caminho):
    texto = open(caminho, encoding="utf-8").read()
    bloco = re.match(r"---\n(.*?)\n---\n", texto, re.S)
    if not bloco:
        raise SystemExit("Sem frontmatter: " + caminho)
    return bloco.group(1)


def main():
    nomes = sorted(n for n in os.listdir(FONTE) if os.path.isfile(os.path.join(FONTE, n, "SKILL.md")))
    for destino in DESTINOS:
        pasta = os.path.join(ROOT, destino)
        if os.path.isdir(pasta):
            for antigo in os.listdir(pasta):
                if antigo.startswith("interago-") and antigo not in nomes:
                    shutil.rmtree(os.path.join(pasta, antigo))
        for nome in nomes:
            alvo = os.path.join(pasta, nome)
            os.makedirs(alvo, exist_ok=True)
            corpo = ("---\n" + frontmatter(os.path.join(FONTE, nome, "SKILL.md")) + "\n---\n\n"
                     "O conteúdo desta skill está em `skills/" + nome + "/SKILL.md`, na raiz do repositório. "
                     "Leia esse arquivo por inteiro (e os arquivos que ele citar) antes de agir.\n")
            with open(os.path.join(alvo, "SKILL.md"), "w", encoding="utf-8") as fh:
                fh.write(corpo)
    print(str(len(nomes)) + " skills espelhadas em " + str(len(DESTINOS)) + " pastas")


if __name__ == "__main__":
    main()
