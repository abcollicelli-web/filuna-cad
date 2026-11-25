"""Visualizador ao vivo: abre a peça no navegador e refaz e confere a cada vez que o arquivo é salvo.

    python -m filuna_cad ver peca.py      # o script recebe o caminho do STL de saída como primeiro argumento
    python -m filuna_cad ver peca.scad    # gerado pelo OpenSCAD
    python -m filuna_cad ver peca.stl     # STL, 3MF, OBJ, GLB ou STEP: só mostra e confere

Roda só na sua máquina (localhost). A página mostra a peça em 3D, a nota, as medidas e cada achado do `validar`.
"""
import json
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .validar import Limites, carregar, validar

PAGINA = Path(__file__).with_name("ver.html")
TEMPO_GERAR = 120


def gerar(fonte, saida):
    """Transforma a fonte em STL. Devolve None se deu certo ou o texto do erro."""
    ext = fonte.suffix.lower()
    if ext == ".py":
        cmd = [sys.executable, str(fonte), str(saida)]
    elif ext == ".scad":
        openscad = shutil.which("openscad")
        if not openscad:
            return "OpenSCAD não encontrado no PATH."
        cmd = [openscad, "--backend=manifold", "-o", str(saida), str(fonte)]
    else:
        carregar(fonte).export(saida)
        return None
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=TEMPO_GERAR, cwd=fonte.parent, check=False)
    if r.returncode or not Path(saida).exists():
        return (r.stderr or r.stdout or "o gerador não gravou a peça").strip()[-2000:]
    return None


class Sessao:
    """Guarda a última peça gerada e o resultado da conferência; refaz quando a fonte muda."""

    def __init__(self, fonte, mesa):
        self.fonte, self.mesa = Path(fonte).resolve(), mesa
        self.pasta = Path(tempfile.mkdtemp(prefix="filuna-ver-"))
        self.stl = self.pasta / "peca.stl"
        self.estado = {"versao": 0, "gerando": True}
        self.trava = threading.Lock()

    def refazer(self):
        with self.trava:
            self.estado = {**self.estado, "gerando": True}
        inicio = time.monotonic()
        provisorio = self.pasta / "nova.stl"
        provisorio.unlink(missing_ok=True)
        conferencia = None
        try:
            erro = gerar(self.fonte, provisorio)
            if not erro:
                provisorio.replace(self.stl)
                conferencia = validar(self.stl, Limites(mesa=self.mesa))
        except (OSError, ValueError, subprocess.TimeoutExpired) as e:
            # Fonte com erro não pode derrubar o visualizador: o erro vai para a página e espera o próximo salvamento.
            erro = f"{type(e).__name__}: {e}"
        with self.trava:
            self.estado = {"versao": self.estado["versao"] + 1, "gerando": False, "erro": erro, "fonte": self.fonte.name,
                           "segundos": round(time.monotonic() - inicio, 2), "conferencia": conferencia}

    def vigiar(self, intervalo=0.5):
        ultimo = object()   # diferente de tudo: a primeira volta sempre gera, até quando o arquivo não existe
        while True:
            try:
                marca = self.fonte.stat().st_mtime
            except FileNotFoundError:
                marca = None
            if marca != ultimo:
                ultimo = marca
                self.refazer()
            time.sleep(intervalo)


def _atendente(sessao):
    class Atendente(BaseHTTPRequestHandler):
        def log_message(self, *args):
            return

        def _enviar(self, corpo, tipo):
            self.send_response(200)
            self.send_header("Content-Type", tipo)
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(corpo)

        def do_GET(self):
            if self.path.startswith("/estado"):
                with sessao.trava:
                    corpo = json.dumps(sessao.estado, ensure_ascii=False).encode()
                self._enviar(corpo, "application/json; charset=utf-8")
            elif self.path.startswith("/peca.stl") and sessao.stl.exists():
                self._enviar(sessao.stl.read_bytes(), "model/stl")
            elif self.path in ("/", "/index.html"):
                self._enviar(PAGINA.read_bytes(), "text/html; charset=utf-8")
            else:
                self.send_error(404)

    return Atendente


def ver(fonte, porta=8765, mesa=(256.0, 256.0, 256.0), abrir=True):
    sessao = Sessao(fonte, mesa)
    threading.Thread(target=sessao.vigiar, daemon=True).start()
    servidor = ThreadingHTTPServer(("localhost", porta), _atendente(sessao))
    endereco = f"http://localhost:{servidor.server_address[1]}/"
    sys.stderr.write(f"Visualizador em {endereco}  (Ctrl+C para sair)\n")
    if abrir:
        import webbrowser

        webbrowser.open(endereco)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        sys.stderr.write("Visualizador encerrado.\n")
    finally:
        servidor.server_close()
        shutil.rmtree(sessao.pasta, ignore_errors=True)
    return {"endereco": endereco}
