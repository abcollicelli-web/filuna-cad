"""Confere o repositório: links relativos que existem, cabeçalho de cada skill e nada privado no que será publicado."""
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
LINK = re.compile(r"\[[^\]]*\]\(([^)#\s]+)(?:#[^)]*)?\)")
PROIBIDO = re.compile(
    r"/srv/filuna|/var/lib/filuna|/opt/filuna|BEGIN [A-Z ]*PRIVATE KEY|ghp_[A-Za-z0-9]{20}|sk-[A-Za-z0-9]{20}"
    r"|[\w.+-]+@(gmail|hotmail|outlook|yahoo)\.com|\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")
TEXTO = {".md", ".py", ".json", ".scad", ".toml", ".yml", ".txt"}
IGNORAR = {".git", "__pycache__", ".pytest_cache", ".aislop"}


def arquivos():
    for caminho in RAIZ.rglob("*"):
        if caminho.is_file() and not IGNORAR & set(caminho.parts):
            yield caminho


def links_quebrados(caminho, texto):
    for alvo in LINK.findall(texto):
        if "://" in alvo or alvo.startswith("mailto:"):
            continue
        if not (caminho.parent / alvo).exists():
            yield f"{caminho.relative_to(RAIZ)}: link quebrado para {alvo}"


def cabecalho_da_skill(caminho, texto):
    m = re.match(r"---\n(.*?)\n---\n", texto, re.S)
    campos = dict(re.findall(r"^(name|description):\s*(.+)$", m.group(1), re.M)) if m else {}
    if campos.get("name") != caminho.parent.name:
        yield f"{caminho.relative_to(RAIZ)}: 'name' precisa ser igual ao nome da pasta"
    if len(campos.get("description", "")) < 80:
        yield f"{caminho.relative_to(RAIZ)}: 'description' curta demais para o assistente saber quando usar"


def main():
    problemas = []
    for caminho in arquivos():
        if caminho.suffix not in TEXTO or caminho.name == Path(__file__).name:
            continue
        texto = caminho.read_text(encoding="utf-8")
        achado = PROIBIDO.search(texto)
        if achado:
            problemas.append(f"{caminho.relative_to(RAIZ)}: conteúdo privado ({achado.group(0)})")
        if caminho.suffix == ".md":
            problemas += links_quebrados(caminho, texto)
        if caminho.name == "SKILL.md":
            problemas += cabecalho_da_skill(caminho, texto)
    for nome in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", ".mcp.json"):
        json.loads((RAIZ / nome).read_text(encoding="utf-8"))
    sys.stdout.write("\n".join(problemas) + ("\n" if problemas else "") + f"problemas: {len(problemas)}\n")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
