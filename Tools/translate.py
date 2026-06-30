import os
import json
from Tools.utils import getConfig


class Translate:
    def __init__(self):
        self.translation = {}
        languages_dir = "Languages"
        if not os.path.isdir(languages_dir):
            return
        for filename in os.listdir(languages_dir):
            if filename.endswith(".json"):
                lang_key = filename[:-5]
                path = os.path.join(languages_dir, filename)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        self.translation[lang_key] = json.load(f)
                except (json.JSONDecodeError, OSError):
                    print(f"Failed to load language file: {filename}")

    def msg(self, guildID, command, message):
        config = getConfig(guildID)
        language = config["language"]
        try:
            return self.translation[language][command][message]
        except (KeyError, TypeError):
            try:
                return self.translation.get("en-US", {}).get(command, {}).get(message, f"Missing: {command}.{message}")
            except (KeyError, TypeError):
                return f"Missing: {command}.{message}"
