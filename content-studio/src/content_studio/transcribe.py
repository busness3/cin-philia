"""Transcription automatique (speech-to-text) des rushs, mot par mot.

Utilise faster-whisper (CTranslate2), avec horodatage par mot — nécessaire
pour synchroniser finement les sous-titres et animer/surligner le mot en
cours de lecture (style TikTok).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional


@dataclass
class Word:
    text: str
    start: float
    end: float


_MODEL_CACHE: dict[str, object] = {}


def _get_model(model_size: str = "small", device: str = "auto", compute_type: str = "auto"):
    """Charge (et met en cache) le modèle faster-whisper.

    Import différé : faster-whisper/ctranslate2 sont des dépendances lourdes,
    on ne veut pas les charger juste pour utiliser le reste du package
    (ex: normalize/subtitles avec un SRT déjà fourni).
    """
    key = f"{model_size}:{device}:{compute_type}"
    if key not in _MODEL_CACHE:
        from faster_whisper import WhisperModel

        _MODEL_CACHE[key] = WhisperModel(model_size, device=device, compute_type=compute_type)
    return _MODEL_CACHE[key]


def words_from_whisper_segments(segments: Iterable) -> list[Word]:
    """Adapte les segments faster-whisper (avec word_timestamps=True) en Word[].

    Séparée de `transcribe()` pour être testable sans modèle réel (segments
    factices en entrée).
    """
    words: list[Word] = []
    for seg in segments:
        seg_words = getattr(seg, "words", None) or []
        for w in seg_words:
            text = w.word.strip()
            if text:
                words.append(Word(text=text, start=float(w.start), end=float(w.end)))
    return words


def transcribe(
    audio_path: str | Path,
    language: str = "fr",
    model_size: str = "small",
) -> list[Word]:
    """Transcrit un rush (ou un fichier audio) et renvoie les mots horodatés."""
    model = _get_model(model_size=model_size)
    segments, _info = model.transcribe(str(audio_path), language=language, word_timestamps=True)
    return words_from_whisper_segments(segments)


@dataclass
class WordGroup:
    words: list[Word]
    start: float
    end: float

    @property
    def text(self) -> str:
        return " ".join(w.text for w in self.words)


def group_words(words: list[Word], mots_par_groupe: int, trailing_pad_s: float = 0.15) -> list[WordGroup]:
    """Regroupe les mots par paquets de N (style légendes TikTok punchy).

    La fin d'un groupe s'étend un peu après le dernier mot (trailing_pad_s)
    mais jamais au-delà du début du groupe suivant, pour éviter tout
    chevauchement d'affichage.
    """
    if mots_par_groupe < 1:
        raise ValueError("mots_par_groupe doit être >= 1")

    groups: list[WordGroup] = []
    for i in range(0, len(words), mots_par_groupe):
        chunk = words[i : i + mots_par_groupe]
        if not chunk:
            continue
        groups.append(WordGroup(words=chunk, start=chunk[0].start, end=chunk[-1].end))

    for i, g in enumerate(groups):
        padded_end = g.end + trailing_pad_s
        if i + 1 < len(groups):
            padded_end = min(padded_end, groups[i + 1].start)
        g.end = max(padded_end, g.start + 0.05)  # jamais une durée nulle/négative

    return groups


def parse_srt(path: str | Path) -> list[WordGroup]:
    """Lit un .srt fourni par Cléa (script déjà écrit) et le convertit en
    WordGroup — utilisé quand `sous_titres` d'une séquence pointe vers un
    fichier au lieu de "auto"."""
    import re

    content = Path(path).read_text(encoding="utf-8")
    blocks = re.split(r"\n\s*\n", content.strip())
    groups: list[WordGroup] = []
    time_re = re.compile(
        r"(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})"
    )

    def _to_s(h, m, s, ms) -> float:
        return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

    for block in blocks:
        lines = [line for line in block.strip().splitlines() if line.strip()]
        if len(lines) < 2:
            continue
        # ligne 0 = index numérique (optionnel selon l'export), ligne suivante
        # contenant "-->" = le timecode ; tout ce qui suit = le texte.
        timecode_idx = next((i for i, line in enumerate(lines) if "-->" in line), None)
        if timecode_idx is None:
            continue
        m = time_re.search(lines[timecode_idx])
        if m is None:
            continue
        start = _to_s(*m.groups()[0:4])
        end = _to_s(*m.groups()[4:8])
        text = " ".join(lines[timecode_idx + 1 :]).strip()
        if not text:
            continue
        fake_word = Word(text=text, start=start, end=end)
        groups.append(WordGroup(words=[fake_word], start=start, end=end))
    return groups
