"""Interface en ligne de commande de content-studio.

Usage :
    python -m content_studio.cli render episodes/mon_episode.yaml
    python -m content_studio.cli list-series
    python -m content_studio.cli check-config diagnostic_serie
"""
from __future__ import annotations

import argparse
import sys

from .config import ConfigError, list_series, resolve_config
from .pipeline import render_episode


def _cmd_render(args: argparse.Namespace) -> int:
    try:
        sortie = render_episode(
            args.episode, keep_intermediates=args.keep_intermediates, work_dir=args.work_dir
        )
    except ConfigError as e:
        print(f"Erreur de config : {e}", file=sys.stderr)
        return 1
    print(f"Vidéo générée : {sortie}")
    return 0


def _cmd_list_series(_args: argparse.Namespace) -> int:
    series = list_series()
    if not series:
        print("Aucune série trouvée dans configs/series/")
        return 0
    for s in series:
        print(s)
    return 0


def _cmd_check_config(args: argparse.Namespace) -> int:
    try:
        resolved = resolve_config(args.series_id)
    except ConfigError as e:
        print(f"Erreur de config : {e}", file=sys.stderr)
        return 1
    print(f"Série : {resolved.serie.nom} ({resolved.serie.id})")
    print(f"  accent         : {resolved.serie.accent}")
    print(f"  CTA de sortie  : {resolved.serie.cta_sortie or '(aucun)'}")
    print(f"  mood musique   : {resolved.serie.audio.mood_musique}")
    print(f"  sous-titres    : {resolved.global_.sous_titres.police}, {resolved.global_.sous_titres.taille_px}px "
          f"(global, mode={resolved.global_.sous_titres.mode_groupement})")
    print(f"  rythme         : transition par défaut = {resolved.global_.rythme.transition_defaut} (global)")
    print("Config valide.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="content-studio")
    sub = parser.add_subparsers(dest="command", required=True)

    p_render = sub.add_parser("render", help="Rendre un épisode à partir de son fichier YAML")
    p_render.add_argument("episode", help="chemin vers episodes/xxx.yaml")
    p_render.add_argument("--keep-intermediates", action="store_true", help="garder les fichiers intermédiaires")
    p_render.add_argument("--work-dir", default=None, help="dossier de travail (défaut: out/.tmp_<nom>)")
    p_render.set_defaults(func=_cmd_render)

    p_list = sub.add_parser("list-series", help="Lister les séries configurées")
    p_list.set_defaults(func=_cmd_list_series)

    p_check = sub.add_parser("check-config", help="Valider et afficher la config résolue d'une série")
    p_check.add_argument("series_id", help="id de la série (nom du fichier dans configs/series/, sans .yaml)")
    p_check.set_defaults(func=_cmd_check_config)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
