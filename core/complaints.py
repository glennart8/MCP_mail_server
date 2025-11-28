"""Hanterar kundklagomål och supportärenden."""

import json
from pathlib import Path


class ComplaintsSystem:
    """Hanterar alla kundklagomål och sparar dem till fil."""

    def __init__(self, file_path: str = "logs/complaints.json"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.complaints = self._load_complaints()

    def _load_complaints(self) -> list:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def _save_complaints(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.complaints, f, ensure_ascii=False, indent=2)

    def log_complaint(self, email: dict) -> dict:
        """Loggar ett nytt klagomål från ett e-postmeddelande."""
        complaint = {
            "from": email["from"],
            "subject": email["subject"],
            "body": email["body"],
            "status": "open"
        }
        print(f"Skapar klagomål: '{complaint['subject']}'")
        self.complaints.append(complaint)
        self._save_complaints()
        return complaint

    def get_open_complaints(self) -> list:
        """Returnerar alla öppna klagomål."""
        return [c for c in self.complaints if c.get("status") == "open"]

    def close_complaint(self, index: int) -> bool:
        """Stänger ett klagomål baserat på index."""
        if 0 <= index < len(self.complaints):
            self.complaints[index]["status"] = "closed"
            self._save_complaints()
            return True
        return False
