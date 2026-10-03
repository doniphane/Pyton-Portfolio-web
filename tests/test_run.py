"""Tests du lanceur de développement.

Ce module teste ``run.py``, qui n'est pas importé par l'application : on le
charge explicitement pour ne pas déclencher le serveur au moment de la collecte.
"""

from __future__ import annotations

import socket

import pytest

from run import DEFAULT_PORT, FALLBACK_PORTS, choisir_port, port_est_libre


@pytest.fixture
def port_occupe():
    """Un socket réellement lié, pour reproduire un port déjà pris."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        s.listen(1)
        yield s.getsockname()[1]


def test_port_libre_detecte(port_occupe):
    assert port_est_libre(port_occupe) is False


def test_port_inconnu_renseigne_comme_libre():
    # Un port que rien n'occupe : on prend un port haut et improbable.
    assert port_est_libre(54321) is True


def test_un_port_occupe_amene_a_un_repli(monkeypatch, capsys, port_occupe):
    """Sur macOS, ControlCenter peut tenir le port 5000 : le serveur doit
    basculer sur un port libre au lieu d'échouer en silence."""
    monkeypatch.setenv("PORT", str(port_occupe))
    # On neutralise la liste de repli pour contrôler le résultat.
    monkeypatch.setattr("run.FALLBACK_PORTS", (54322, 54323))

    port = choisir_port()
    assert port == 54322
    assert "déjà utilisé" in capsys.readouterr().err


def test_le_port_demande_est_respecte_sil_est_libre(monkeypatch, capsys):
    monkeypatch.setenv("PORT", "54324")
    assert choisir_port() == 54324
    assert capsys.readouterr().err == ""


def test_aucun_port_libre_echoue_proprement(monkeypatch, port_occupe):
    monkeypatch.setenv("PORT", str(port_occupe))
    monkeypatch.setattr("run.FALLBACK_PORTS", (port_occupe,))
    with pytest.raises(SystemExit):
        choisir_port()


def test_port_par_defaut_evite_le_5000():
    """5000 est disputé par AirPlay Receiver sur macOS : le port par défaut
    ne doit pas l'être, sinon le site répond une fois sur deux."""
    assert DEFAULT_PORT != 5000
    assert 5000 not in FALLBACK_PORTS


def test_aucun_repli_ne_vise_le_5000():
    """Idem pour les ports de repli : aucun ne doit être 5000."""
    assert all(p != 5000 for p in FALLBACK_PORTS)
