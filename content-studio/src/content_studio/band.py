"""Bandeau titre — gabarit partagé entre la couverture statique (cover.py) et
le titre incrusté en ouverture/sortie de vidéo (pipeline.py) : bandeau crème,
bloc d'accent, titre sur 1-2 lignes en chocolat. Même positionnement partout,
pixel pour pixel, défini une seule fois dans `configs/global.yaml` (`couverture`).

Approximations connues (cf. README) :
- la position verticale du texte utilise `text_h` (hauteur de la boîte du
  glyphe, descendantes incluses) comme repère de ligne de base — un `g`/`p`/`y`
  fait donc paraître la ligne de base légèrement plus haute que la valeur
  pixel-exacte de la config.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from . import ffmpeg_utils as ff
from .drawtext import drawtext_filter, hex_to_ffmpeg_color, write_textfile
from .models import GabaritCouverture, VideoConfig


def split_title_lines(texte: str) -> tuple[str, str]:
    """Coupe un titre en (ligne1, ligne2). Respecte un retour à la ligne
    manuel (\\n) si présent ; sinon répartit les mots en deux moitiés."""
    if "\n" in texte:
        parts = texte.split("\n", 1)
        return parts[0].strip(), parts[1].strip()
    words = texte.split()
    if len(words) <= 1:
        return texte.strip(), ""
    mid = (len(words) + 1) // 2
    return " ".join(words[:mid]), " ".join(words[mid:])


def band_filters(
    gabarit: GabaritCouverture,
    accent_hex: str,
    titre_font_path: str | Path,
    titre_taille_px: int,
    texte: str,
    work_dir: str | Path,
    label_prefix: str,
    enable_expr: Optional[str] = None,
) -> list[str]:
    """Renvoie la liste de filtres ffmpeg (drawbox/drawtext) dessinant le
    bandeau + bloc accent + titre. `enable_expr` (ex: "between(t\\,0.3\\,2.3)")
    restreint l'affichage à une fenêtre temporelle ; None = toujours visible
    (cas de la couverture statique)."""
    work_dir = Path(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    bandeau, bloc, titre = gabarit.bandeau, gabarit.bloc_accent, gabarit.titre
    # Pas de quotes autour de l'expression : cohérent avec le reste du code
    # (overlays.py) où les virgules internes à between(...) sont juste
    # échappées en \, — évite les pièges de parsing observés avec des
    # guillemets dans les valeurs de filtres ffmpeg.
    enable_suffix = f":enable={enable_expr}" if enable_expr else ""

    filters = [
        f"drawbox=x={bandeau.x}:y={bandeau.y}:w={bandeau.largeur}:h={bandeau.hauteur}:"
        f"color={hex_to_ffmpeg_color(bandeau.couleur_fond)}:t=fill{enable_suffix}",
        f"drawbox=x={bloc.x}:y={bloc.y}:w={bloc.largeur}:h={bloc.hauteur}:"
        f"color={hex_to_ffmpeg_color(accent_hex)}:t=fill{enable_suffix}",
    ]

    ligne1, ligne2 = split_title_lines(texte)
    textfile1 = write_textfile(ligne1, work_dir / f"{label_prefix}_titre_l1.txt")
    filters.append(
        drawtext_filter(
            textfile_path=textfile1,
            fontfile_path=titre_font_path,
            fontsize=titre_taille_px,
            fontcolor=hex_to_ffmpeg_color(titre.couleur_texte),
            x=str(titre.x),
            y=f"{titre.baseline_ligne1_y}-text_h",
            enable=enable_expr,
        )
    )
    if ligne2:
        textfile2 = write_textfile(ligne2, work_dir / f"{label_prefix}_titre_l2.txt")
        filters.append(
            drawtext_filter(
                textfile_path=textfile2,
                fontfile_path=titre_font_path,
                fontsize=titre_taille_px,
                fontcolor=hex_to_ffmpeg_color(titre.couleur_texte),
                x=str(titre.x),
                y=f"{titre.baseline_ligne2_y}-text_h",
                enable=enable_expr,
            )
        )

    return filters


def apply_animated_band_to_video(
    video_path: str | Path,
    output_path: str | Path,
    gabarit: GabaritCouverture,
    video_cfg: VideoConfig,
    clip_anime_path: str | Path,
    start_s: float,
    duration_s: float,
) -> Path:
    """Incruste un bandeau **animé** (clip vidéo pré-rendu, ex: HyperFrames)
    à la place du bandeau statique (`band_filters`). Le clip doit déjà faire
    la taille exacte du bandeau (`gabarit.bandeau.largeur` x `hauteur`,
    fond opaque -- pas de transparence nécessaire) : il est simplement posé
    à la position du bandeau, actif entre `start_s` et `start_s + duration_s`.
    """
    ff.check_ffmpeg_available()
    video_path, output_path = Path(video_path), Path(output_path)
    clip_anime_path = Path(clip_anime_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    bandeau = gabarit.bandeau
    end_s = start_s + duration_s
    enable_expr = f"between(t\\,{start_s}\\,{end_s})"
    filter_complex = (
        f"[0:v][1:v]overlay=x={bandeau.x}:y={bandeau.y}:"
        f"enable='{enable_expr}':eof_action=pass[vout]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-itsoffset", str(start_s), "-i", str(clip_anime_path),
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "0:a",
        "-c:v", video_cfg.codec_video, "-crf", str(video_cfg.crf), "-preset", video_cfg.preset,
        "-c:a", "copy",
        str(output_path),
    ]
    ff.run(cmd)
    return output_path


def apply_band_to_video(
    video_path: str | Path,
    output_path: str | Path,
    gabarit: GabaritCouverture,
    accent_hex: str,
    titre_font_path: str | Path,
    titre_taille_px: int,
    texte: str,
    video_cfg: VideoConfig,
    start_s: float,
    duration_s: float,
    work_dir: str | Path,
    label_prefix: str = "band",
) -> Path:
    """Incruste le bandeau (fond + bloc accent + titre) sur une vidéo
    existante, actif uniquement entre `start_s` et `start_s + duration_s`."""
    ff.check_ffmpeg_available()
    video_path, output_path = Path(video_path), Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    end_s = start_s + duration_s
    enable_expr = f"between(t\\,{start_s}\\,{end_s})"
    filters = band_filters(
        gabarit, accent_hex, titre_font_path, titre_taille_px, texte,
        work_dir, label_prefix, enable_expr=enable_expr,
    )
    vf = ",".join(filters)

    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-vf", vf,
        "-c:v", video_cfg.codec_video, "-crf", str(video_cfg.crf), "-preset", video_cfg.preset,
        "-c:a", "copy",
        str(output_path),
    ]
    ff.run(cmd)
    return output_path
