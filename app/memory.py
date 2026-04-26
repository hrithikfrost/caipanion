import json
from pathlib import Path
from typing import Any


class MemoryStore:
    """Stores a short conversation history for each Telegram chat in a JSON file."""

    def __init__(self, file_path: Path, max_messages: int = 10) -> None:
        self.file_path = file_path
        self.max_messages = max_messages
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._save({})

    def add_message(self, chat_id: int, role: str, text: str) -> None:
        data = self._load()
        chat_key = str(chat_id)
        history = data.setdefault(chat_key, {"messages": [], "profile": {}})

        history["messages"].append({"role": role, "text": text})
        history["messages"] = history["messages"][-self.max_messages :]

        self._save(data)

    def get_messages(self, chat_id: int) -> list[dict[str, str]]:
        data = self._load()
        chat_data = data.get(str(chat_id), {})
        return chat_data.get("messages", [])

    def remember_user(self, chat_id: int, username: str | None, first_name: str | None) -> None:
        data = self._load()
        chat_key = str(chat_id)
        chat_data = data.setdefault(chat_key, {"messages": [], "profile": {}})
        chat_data["profile"] = {
            "username": username or "",
            "first_name": first_name or "",
        }
        self._save(data)

    def get_known_chat_ids(self) -> list[int]:
        data = self._load()
        return [int(chat_id) for chat_id in data.keys()]

    def get_profile(self, chat_id: int) -> dict[str, str]:
        data = self._load()
        chat_data = data.get(str(chat_id), {})
        return chat_data.get("profile", {})

    def _load(self) -> dict[str, Any]:
        with self.file_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _save(self, data: dict[str, Any]) -> None:
        with self.file_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=True, indent=2)
