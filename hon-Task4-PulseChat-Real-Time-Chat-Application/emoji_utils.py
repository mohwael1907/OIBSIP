import re

# Comprehensive map of common emoji shortcodes to Unicode characters
EMOJI_MAP = {
    ":smile:": "😄",
    ":grinning:": "😀",
    ":laughing:": "😆",
    ":joy:": "😂",
    ":rofl:": "🤣",
    ":wink:": "😉",
    ":blush:": "😊",
    ":heart_eyes:": "😍",
    ":cool:": "😎",
    ":thinking:": "🤔",
    ":raised_eyebrow:": "🤨",
    ":neutral:": "😐",
    ":expressionless:": "😑",
    ":smirk:": "😏",
    ":unamused:": "😒",
    ":pensive:": "😔",
    ":sleepy:": "😪",
    ":sob:": "😭",
    ":screaming:": "😱",
    ":angry:": "😡",
    ":party:": "🎉",
    ":tada:": "🎉",
    ":fire:": "🔥",
    ":heart:": "❤️",
    ":blue_heart:": "💙",
    ":sparkles:": "✨",
    ":star:": "⭐",
    ":thumbsup:": "👍",
    ":thumbsdown:": "👎",
    ":clap:": "👏",
    ":pray:": "🙏",
    ":wave:": "👋",
    ":rocket:": "🚀",
    ":check:": "✅",
    ":x:": "❌",
    ":warning:": "⚠️",
    ":bulb:": "💡",
    ":coffee:": "☕",
    ":beer:": "🍺",
    ":pizza:": "🍕",
    ":cake:": "🎂",
    ":eyes:": "👀",
    ":100:": "💯",
    ":poop:": "💩",
    ":ghost:": "👻",
    ":robot:": "🤖",
    ":alien:": "👽",
    ":bug:": "🐛",
    ":computer:": "💻",
    ":shield:": "🛡️",
    ":lock:": "🔒",
}

# Regex pattern matching :shortcode:
EMOJI_PATTERN = re.compile(r":([a-zA-Z0-9_+-]+):")


def parse_emojis(text: str) -> str:
    """
    Replace all emoji shortcodes in text with their corresponding Unicode characters.
    Unmatched shortcodes are left unchanged.
    """
    if not text:
        return text

    def replacer(match):
        code = match.group(0)
        return EMOJI_MAP.get(code, code)

    return EMOJI_PATTERN.sub(replacer, text)


def get_emoji_list() -> list[dict[str, str]]:
    """Return list of available shortcodes and Unicode pairs for UI pickers."""
    return [{"shortcode": code, "unicode": uni} for code, uni in EMOJI_MAP.items()]
