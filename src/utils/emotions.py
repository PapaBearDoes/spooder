"""
============================================================================
Spooder — Emotive Spider Bot for Fluxer
The Alphabet Cartel
============================================================================

MISSION:
    Give every chat a tiny spider friend that expresses emotions
    through ASCII art, one command at a time.

============================================================================
Emotion map and spider rendering utilities.
Defines all supported emotions and their eye patterns, plus the spider
assembly logic using Unicode box-drawing characters for legs.
----------------------------------------------------------------------------
FILE VERSION: v1.0.0
LAST MODIFIED: 2026-04-05
COMPONENT: spooder
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/PapaBearDoes/spooder
============================================================================
"""

# ---------------------------------------------------------------------------
# Spider leg characters — double-escaped backslashes
# Fluxer's markdown engine treats \ as an escape character, so we send \\
# in the REST payload to render a single \ in chat.
# ---------------------------------------------------------------------------
LEG_PAIR = "/\\\\"

# Full leg groups (two pairs per side)
LEGS_LEFT  = f"{LEG_PAIR}{LEG_PAIR}"
LEGS_RIGHT = f"{LEG_PAIR}{LEG_PAIR}"

# ---------------------------------------------------------------------------
# Emotion → Eye Pattern Map
#
# Each emotion maps to a two-character string representing the spider's eyes.
# Add new emotions here — the handler picks them up automatically.
# ---------------------------------------------------------------------------
EMOTIONS: dict[str, str] = {
    # --- Core emotions ---
    "happy":      "^^",
    "sad":        ";;",
    "angry":      "><",
    "love":       "♥♥",
    "surprised":  "OO",

    # --- Expressive ---
    "wink":       "^~",
    "sleepy":     "--",
    "dead":       "XX",
    "confused":   "??",
    "scared":     "°°",
    "shy":        "..",
    "excited":    "**",
    "suspicious": "¬¬",
    "smug":       "≖≖",
    "dizzy":      "@@",
    "crying":     "TT",
    "sparkle":    "✧✧",
    "cool":       "■■",
    "blank":      "  ",
    "derp":       "◉◉",
    "uwu":        "◡◡",
}

# Default eyes when no emotion or unknown emotion is provided
DEFAULT_EYES = "^^"


def build_spider(eyes: str, message: str | None = None) -> str:
    """
    Assemble the full spider string.

    Args:
        eyes: Two-character eye pattern from EMOTIONS map.
        message: Optional message text. If provided, appended after arrow.

    Returns:
        Rendered spider string ready to post to chat.
    """
    spider = f"{LEGS_LEFT}{eyes}{LEGS_RIGHT}"

    if message:
        return f"{spider} -> Spooder Said: {message}"
    return spider


def get_eyes(emotion: str) -> str | None:
    """
    Look up the eye pattern for a given emotion.

    Args:
        emotion: The emotion name (case-insensitive).

    Returns:
        The eye pattern string, or None if the emotion is not recognized.
    """
    return EMOTIONS.get(emotion.lower())


def list_emotions() -> str:
    """
    Build a formatted string listing all available emotions and their eyes.

    Returns:
        Multi-line string suitable for posting as a help message.
    """
    lines = ["Available emotions:"]
    for name, eyes in sorted(EMOTIONS.items()):
        spider = build_spider(eyes)
        lines.append(f"  {name:<14} {spider}")
    return "\n".join(lines)


__all__ = [
    "EMOTIONS", "DEFAULT_EYES", "LEG_PAIR",
    "build_spider", "get_eyes", "list_emotions",
]
