# Cross-platform content renderer for Dreamcobots.
# Dynamically adapts content for smart TVs, computers, phones, and other electronics.

PLATFORM_PROFILES = {
    "smart_tv": {
        "max_width": 80,
        "supports_emoji": True,
        "font_scale": "large",
        "layout": "landscape",
    },
    "computer": {
        "max_width": 120,
        "supports_emoji": True,
        "font_scale": "normal",
        "layout": "landscape",
    },
    "phone": {
        "max_width": 40,
        "supports_emoji": True,
        "font_scale": "small",
        "layout": "portrait",
    },
    "tablet": {
        "max_width": 60,
        "supports_emoji": True,
        "font_scale": "normal",
        "layout": "portrait",
    },
    "other": {
        "max_width": 60,
        "supports_emoji": False,
        "font_scale": "normal",
        "layout": "landscape",
    },
}


class CrossPlatformRenderer:
    """
    Renders content optimized for different device types.

    Supports: smart_tv, computer, phone, tablet, other.
    """

    def __init__(self, platform="computer"):
        self.platform = platform.lower()
        self.profile = PLATFORM_PROFILES.get(self.platform, PLATFORM_PROFILES["other"])

    def _strip_emoji(self, text):
        """Remove non-ASCII characters (including emoji) for platforms that don't support them."""
        return text.encode("ascii", "ignore").decode("ascii").strip()

    def _wrap_text(self, text, width):
        """Wrap text to the given character width."""
        words = text.split()
        lines = []
        current = []
        current_len = 0
        for word in words:
            if current_len + len(word) + (1 if current else 0) > width:
                lines.append(" ".join(current))
                current = [word]
                current_len = len(word)
            else:
                current.append(word)
                current_len += len(word) + (1 if current else 0)
        if current:
            lines.append(" ".join(current))
        return "\n".join(lines)

    def render(self, content, content_type="text"):
        """
        Render content for the current platform.

        Parameters
        ----------
        content : str | dict
            The content to render. Dicts are formatted into readable strings.
        content_type : str
            One of: 'text', 'movie', 'fact', 'joke', 'status'.
        """
        if isinstance(content, dict):
            content = self._dict_to_str(content, content_type)

        if not self.profile["supports_emoji"]:
            content = self._strip_emoji(content)

        max_width = self.profile["max_width"]
        rendered = self._wrap_text(content, max_width)

        border = "=" * min(max_width, 60)
        platform_label = f"[{self.platform.upper()}]"
        return f"{border}\n{platform_label}\n{rendered}\n{border}"

    def _dict_to_str(self, data, content_type):
        """Convert a dict to a human-readable string based on content type."""
        if content_type == "movie":
            genres = ", ".join(data.get("genre", []))
            return (
                f"🎬 {data.get('title', 'Unknown')} ({data.get('year', '?')})\n"
                f"Director: {data.get('director', 'Unknown')}\n"
                f"Genre: {genres}\n"
                f"Rating: {data.get('rating', '?')}/10\n"
                f"{data.get('description', '')}"
            )
        if content_type == "status":
            lines = [f"{k}: {v}" for k, v in data.items()]
            return "\n".join(lines)
        return str(data)

    def render_list(self, items, content_type="text"):
        """Render a list of content items for the current platform."""
        separator = "-" * min(self.profile["max_width"], 40)
        rendered_items = [self.render(item, content_type) for item in items]
        return f"\n{separator}\n".join(rendered_items)
