"""Exécution en développement : ``python run.py``.

En production, on passe par un serveur WSGI — voir README.md.

Deux précautions liées au port, dictées par macOS :

* le port 5000 est pris par le « Récepteur AirPlay » d'Apple (ControlCenter) ;
* surtout, macOS autorise deux programmes à se lier au même port
  (``SO_REUSEPORT``) et répartit le trafic entre les deux. Un serveur démarré
  sur un port déjà occupé répond donc une fois sur deux, et l'autre fois on
  obtient la page d'erreur de l'autre application.

D'où le port par défaut à 5001, et la vérification qui suit.
"""

from __future__ import annotations

import errno
import os
import socket
import sys

from app import create_app

app = create_app()

#: 5000 est disputé par AirPlay Receiver sur macOS : on l'évite.
DEFAULT_PORT = 5001
FALLBACK_PORTS = (5002, 5003, 5050, 8080)


def port_est_libre(port: int, hote: str = "127.0.0.1") -> bool:
    """Vrai si rien n'écoute déjà sur ce port.

    On tente une liaison réelle : c'est la seule façon fiable, l'appel système
    renvoyant ``EADDRINUSE`` si le port est pris, y compris par un processus
    déjà resident.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as essai:
        essai.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            essai.bind((hote, port))
        except OSError as exc:
            if exc.errno in (errno.EADDRINUSE, errno.EACCES):
                return False
            raise
    return True


def choisir_port() -> int:
    """Renvoie le port demandé, ou le premier port libre disponible."""
    demande = int(os.environ.get("PORT", DEFAULT_PORT))
    if port_est_libre(demande):
        return demande

    print(
        f"\n  Le port {demande} est déjà utilisé par un autre programme.\n"
        "  Rappel : sur macOS, le port 5000 est souvent pris par le "
        "« Récepteur AirPlay ».\n",
        file=sys.stderr,
    )
    for candidat in FALLBACK_PORTS:
        if port_est_libre(candidat):
            print(f"  → Démarrage sur le port {candidat} à la place.\n", file=sys.stderr)
            return candidat

    print(
        "  Aucun port libre trouvé. Libère-en un, ou impose un autre :\n"
        "      PORT=5050 python run.py\n",
        file=sys.stderr,
    )
    raise SystemExit(1)


if __name__ == "__main__":
    hote = os.environ.get("HOST", "127.0.0.1")
    port = choisir_port()
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"

    print(f"  http://{hote}:{port}\n")
    app.run(host=hote, port=port, debug=debug)
