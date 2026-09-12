"""Brique 6 : transitions entre séquences (xfade vidéo + acrossfade audio).

Les clips donnés en entrée doivent déjà être au même format (résolution/fps/
codec) — c'est le rôle de la brique normalisation en amont. `cut` réalise une
simple concaténation (pas de recouvrement) ; les autres transitions
recouvrent la fin d'un clip et le début du suivant sur `transition_duration_s`.
"""
from __future__ import annotations

from pathlib import Path

from . import ffmpeg_utils as ff
from .models import VideoConfig

_XFADE_MAP = {
    "fade": "fade",
    "slide": "slideleft",
    "zoom": "zoomin",
}


def concat_with_transitions(
    clips: list[str | Path],
    transitions: list[str],
    transition_duration_s: float,
    output_path: str | Path,
    video_cfg: VideoConfig,
) -> Path:
    """Assemble une liste de clips avec une transition entre chaque paire.

    `transitions` doit contenir exactement `len(clips) - 1` valeurs, parmi
    "cut", "fade", "slide", "zoom".
    """
    clips = [Path(c) for c in clips]
    if not clips:
        raise ValueError("au moins un clip est requis")
    if len(transitions) != len(clips) - 1:
        raise ValueError(
            f"il faut exactement {len(clips) - 1} transitions pour {len(clips)} clips "
            f"(reçu {len(transitions)})"
        )

    ff.check_ffmpeg_available()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if len(clips) == 1:
        cmd = ["ffmpeg", "-y", "-i", str(clips[0]), "-c", "copy", str(output_path)]
        ff.run(cmd)
        return output_path

    durations = [ff.probe(c).duration for c in clips]

    cmd = ["ffmpeg", "-y"]
    for c in clips:
        cmd += ["-i", str(c)]

    filter_parts: list[str] = []
    # Uniformise la timebase de chaque entrée : sans ça, le filtre concat
    # (qui repasse en microsecondes) et les flux bruts (timebase native du
    # conteneur) ne partagent plus la même base de temps, et xfade refuse de
    # s'enchaîner derrière un concat ("timebase do not match").
    for idx in range(len(clips)):
        filter_parts.append(f"[{idx}:v]settb=AVTB[v{idx}n]")
        filter_parts.append(f"[{idx}:a]asettb=AVTB[a{idx}n]")
    cur_v, cur_a = "v0n", "a0n"
    cur_duration = durations[0]

    for i, trans in enumerate(transitions):
        next_idx = i + 1
        next_v, next_a = f"v{next_idx}n", f"a{next_idx}n"
        out_v, out_a = f"v{next_idx}", f"a{next_idx}"

        if trans == "cut":
            filter_parts.append(f"[{cur_v}][{next_v}]concat=n=2:v=1:a=0[{out_v}]")
            filter_parts.append(f"[{cur_a}][{next_a}]concat=n=2:v=0:a=1[{out_a}]")
            cur_duration = cur_duration + durations[next_idx]
        else:
            xfade_type = _XFADE_MAP.get(trans)
            if xfade_type is None:
                raise ValueError(f"transition inconnue : {trans!r} (attendu cut/fade/slide/zoom)")
            offset = max(cur_duration - transition_duration_s, 0.0)
            filter_parts.append(
                f"[{cur_v}][{next_v}]xfade=transition={xfade_type}:"
                f"duration={transition_duration_s}:offset={offset}[{out_v}]"
            )
            filter_parts.append(f"[{cur_a}][{next_a}]acrossfade=d={transition_duration_s}[{out_a}]")
            cur_duration = offset + durations[next_idx]

        cur_v, cur_a = out_v, out_a

    filter_complex = ";".join(filter_parts)
    cmd += [
        "-filter_complex", filter_complex,
        "-map", f"[{cur_v}]", "-map", f"[{cur_a}]",
        "-c:v", video_cfg.codec_video, "-crf", str(video_cfg.crf), "-preset", video_cfg.preset,
        "-c:a", video_cfg.codec_audio, "-b:a", video_cfg.bitrate_audio,
        "-pix_fmt", "yuv420p",
        str(output_path),
    ]
    ff.run(cmd)
    return output_path
