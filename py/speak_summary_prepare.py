#!/usr/bin/env python3
"""
Build JSON payload for POST /say from Cursor hook stdin.

v2: delegates to aftertone.prepare; re-exports helpers for unit tests.
"""

from aftertone.prepare import main
from aftertone.spoken_tag import (
    last_spoken_summary_span as _last_spoken_summary_span,
    parse_spoken_summary as _parse_spoken_summary,
    without_spoken_block as _without_spoken_block,
)
from aftertone.text_utils import (
    clamp as _clamp,
    code_fence_fraction as _code_fence_fraction,
    demote_code_fences as _demote_code_fences,
    heuristic_spoken as _heuristic_spoken,
    in_quiet_hours as _in_quiet_hours,
    is_low_substance_sentence as _is_low_substance_sentence,
    parse_hhmm as _parse_hhmm,
    plain_excerpt as _plain_excerpt,
    split_sentences as _split_sentences,
    spoken_tag_to_speakable as _spoken_tag_to_speakable,
    strip_markdownish as _strip_markdownish,
)

_parse_spoken_summary = _parse_spoken_summary


def _extract_spoken_summary(raw: str) -> str | None:
    body, _state = _parse_spoken_summary(raw)
    return body


if __name__ == "__main__":
    main()
