"""Enkel konversationshistorik sparad i JSON-fil.

Sparar alla konversationer per kund så att AI:n kan se tidigare dialog.
Filen conversations.json kan läsas/redigeras manuellt vid behov.
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Sökväg till historik-filen (i samma mapp som projektet)
CONVERSATIONS_FILE = Path(__file__).parent.parent / "conversations.json"


def _load_conversations() -> dict:
    """Laddar konversationer från fil."""
    if CONVERSATIONS_FILE.exists():
        try:
            with open(CONVERSATIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def _save_conversations(data: dict):
    """Sparar konversationer till fil."""
    with open(CONVERSATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_message(email: str, role: str, message: str, subject: str = ""):
    """Lägger till ett meddelande i konversationshistoriken.

    Args:
        email: Kundens e-postadress
        role: "customer" eller "agent"
        message: Meddelandetext
        subject: Ämnesrad (valfritt)
    """
    conversations = _load_conversations()

    if email not in conversations:
        conversations[email] = []

    conversations[email].append({
        "timestamp": datetime.now().isoformat(),
        "role": role,
        "subject": subject,
        "message": message
    })

    _save_conversations(conversations)


def get_history(email: str, max_messages: int = 10) -> list:
    """Hämtar konversationshistorik för en kund.

    Args:
        email: Kundens e-postadress
        max_messages: Max antal meddelanden att hämta

    Returns:
        Lista med meddelanden (senaste först)
    """
    conversations = _load_conversations()
    history = conversations.get(email, [])
    return history[-max_messages:]  # Senaste N meddelanden


def format_history_for_prompt(email: str, max_messages: int = 5) -> str:
    """Formaterar historik som text för AI-prompten.

    Args:
        email: Kundens e-postadress
        max_messages: Max antal meddelanden att inkludera

    Returns:
        Formaterad text eller tom sträng om ingen historik
    """
    history = get_history(email, max_messages)

    if not history:
        return ""

    lines = ["=== TIDIGARE KONVERSATION MED DENNA KUND ==="]
    for msg in history:
        timestamp = msg["timestamp"][:16].replace("T", " ")  # YYYY-MM-DD HH:MM
        role = "KUND" if msg["role"] == "customer" else "VI"
        subject = f" [{msg['subject']}]" if msg.get("subject") else ""
        lines.append(f"\n[{timestamp}] {role}{subject}:")
        lines.append(msg["message"][:500])  # Begränsa längd

    lines.append("\n=== SLUT PÅ HISTORIK ===\n")
    return "\n".join(lines)


def clear_history(email: str = None):
    """Rensar historik för en kund eller alla.

    Args:
        email: Kundens e-post, eller None för att rensa allt
    """
    if email is None:
        _save_conversations({})
    else:
        conversations = _load_conversations()
        if email in conversations:
            del conversations[email]
            _save_conversations(conversations)
