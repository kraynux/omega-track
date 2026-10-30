# Copyright (c) 2026 kraynux - Licence MIT
"""Point d'entree du package (`python -m omega_track` et le script console
`omega-track`). Dispatche vers la TUI (aucun argument) ou la CLI (au moins
un argument) - meme patron que omega-scan/omega-stress/omega-check
(D-007/D-008)."""
from __future__ import annotations

import sys


def install_language() -> None:
    """Langue de l'interface installee AVANT d'importer la TUI (plan i18n de la suite §5) :
    les textes traduits au chargement d'un module (raccourcis, titres) sont deja dans la
    bonne langue. Jamais pour la ligne de commande (R3 : elle reste en francais)."""
    import os

    from omega_lib.infrastructure.terminal.detector import SystemTerminalDetector

    from omega_track.infrastructure.config import paths
    from omega_track.infrastructure.config.json_settings_loader import JsonSettingsRepository
    from omega_track.shared.i18n import LANGUAGE

    LANGUAGE.install(
        settings_store=JsonSettingsRepository(paths.default_settings_path(paths.resolve_var_dir())),
        environ=os.environ,
        terminal_family=SystemTerminalDetector().detect().family,
    )


def restart_for_language(code: str) -> None:  # pragma: no cover - remplace le processus
    """Meme Python, meme module : seule l'interface redemarre, dans la langue choisie."""
    import os

    from omega_track.shared.i18n import LANGUAGE

    LANGUAGE.prepare_restart_environment(os.environ, code)
    os.execv(sys.executable, [sys.executable, "-m", "omega_track"])


def main(argv: list[str] | None = None) -> int:
    effective_argv = sys.argv[1:] if argv is None else argv
    is_tui = not effective_argv
    if is_tui:
        install_language()

    from omega_track.app.bootstrap import bootstrap

    # console_logging=False sous le TUI : Textual controle l'ecran en mode
    # alternatif, une ecriture de log directe sur stderr corromprait son
    # rendu (voir app/bootstrap.py).
    container = bootstrap(console_logging=not is_tui)
    pending_language: str | None = None
    try:
        if is_tui:
            from omega_track.interfaces.tui.app import OmegaTrackApp

            app = OmegaTrackApp(container)
            app.run()
            pending_language = app.pending_language
        else:
            from omega_track.interfaces.cli.main import run as run_cli

            return run_cli(container, effective_argv)
    finally:
        container.close()
    if pending_language is not None:
        restart_for_language(pending_language)  # apres container.close() : base fermee proprement
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
