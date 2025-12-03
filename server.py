"""
MCP Server för Bengtssons Trävaror - E-posthantering.

Denna server exponerar verktyg för att hantera inkommande mail:
- Hämta e-post
- Hantera supportärenden
- Hantera försäljningsförfrågningar
- Hantera materialberäkningar
- Hantera mötesförfrågningar
"""

import os
import json
from mcp.server.fastmcp import FastMCP

from core.autoresponder import GmailClient
from core.products import PRODUCTS
from core.test_data import FAKE_INBOX
from core.conversations import add_message, format_history_for_prompt

# Konfiguration via miljövariabler
SEND_EMAILS = os.environ.get("SEND_REAL_EMAILS", "false").lower() == "true"
USE_GMAIL = os.environ.get("USE_GMAIL", "false").lower() == "true"
MANAGER_EMAIL = os.environ.get("MANAGER_EMAIL", "")

# Skapa MCP-server
mcp = FastMCP("bengtssons-travaror")

# Initiera system
_fake_inbox = FAKE_INBOX.copy()  # Kopia som töms vid hämtning

# Lazy-loading för Gmail API
_gmail_client = None

def get_gmail_client():
    global _gmail_client
    if _gmail_client is None:
        _gmail_client = GmailClient()
    return _gmail_client


# ==================== RESOURCES ====================

@mcp.resource("products://catalog")
def get_product_catalog() -> str:
    """Returnerar hela produktkatalogen med priser och dimensioner."""
    catalog_lines = []
    for name, (price, dimension) in PRODUCTS.items():
        dim_str = f"{dimension} m/kvm" if dimension else "styck"
        catalog_lines.append(f"{name}: {price} kr ({dim_str})")
    return "\n".join(catalog_lines)


# ==================== TOOLS ====================

@mcp.tool()
def get_unread_emails() -> str:
    """
    Hämtar olästa e-postmeddelanden från inkorgen.

    Returnerar en lista med e-post i JSON-format med fälten:
    - from: avsändarens e-postadress
    - subject: ämnesrad
    - body: meddelandetext

    Använder Gmail API om USE_GMAIL=true, annars testdata.
    """
    global _fake_inbox

    if USE_GMAIL:
        gmail = get_gmail_client()
        emails = gmail.get_unread_emails()
        # Markera som lästa
        for email in emails:
            if 'id' in email:
                gmail.mark_as_read(email['id'])
    else:
        emails = _fake_inbox.copy()
        _fake_inbox.clear()

    if not emails:
        return json.dumps({"message": "Inga nya mail"}, ensure_ascii=False)
    return json.dumps(emails, ensure_ascii=False, indent=2)


@mcp.tool()
def handle_support_email(from_email: str, subject: str, body: str) -> str:
    """
    Hanterar ett supportärende/klagomål komplett:
    1. Sparar kundens meddelande i historik
    2. Genererar AI-svar (med konversationshistorik)
    3. Skickar svar till kunden

    Returns:
        Bekräftelse på vad som gjordes
    """
    from core.agents import ComplaintAgent

    # 1. Spara kundens meddelande i historik
    add_message(from_email, "customer", body, subject)

    # 2. Hämta tidigare konversation och generera svar
    email = {"from": from_email, "subject": subject, "body": body}
    history = format_history_for_prompt(from_email)
    agent = ComplaintAgent()
    response_body = agent.write_response_to_complaint(email, history)

    # 3. Skicka svar (om aktiverat)
    if SEND_EMAILS:
        try:
            gmail = get_gmail_client()
            gmail._send_email(from_email, f"Re: {subject}", response_body)
            # Spara vårt svar i historik
            add_message(from_email, "agent", response_body, f"Re: {subject}")
            return f"Supportärende hanterat för {from_email}: Ärende skapat + svar skickat"
        except Exception as e:
            return f"Supportärende skapat men kunde inte skicka svar: {e}"
    else:
        # Spara även i dry-run för testning
        add_message(from_email, "agent", response_body, f"Re: {subject}")
        return f"[DRY-RUN] Supportärende hanterat för {from_email}: Ärende skapat (mail EJ skickat)"


@mcp.tool()
def handle_sales_email(from_email: str, subject: str, product_query: str) -> str:
    """
    Hanterar en försäljningsförfrågan komplett:
    1. Söker efter produkter
    2. Formaterar snyggt svar
    3. Skickar svar till kunden

    Args:
        product_query: Sökterm för produkter (t.ex. "plywood", "regel")

    Returns:
        Bekräftelse på vad som gjordes
    """
    # 1. Sök produkter
    query_normalized = product_query.lower().replace(" ", "_")
    matches = []

    for name, (price, dimension) in PRODUCTS.items():
        name_lower = name.lower()
        if query_normalized in name_lower or product_query.lower().replace("_", " ") in name_lower.replace("_", " "):
            dim_str = f"{dimension} m/kvm" if dimension else "styck"
            matches.append({
                "name": name,
                "price": price,
                "dimension": dim_str
            })

    # 2. Formatera svar
    if matches:
        product_lines = []
        for p in matches:
            product_lines.append(f"• {p['name'].replace('_', ' ')}: {p['price']} kr ({p['dimension']})")
        product_text = "\n".join(product_lines)
    else:
        product_text = "Tyvärr hittade vi inga matchande produkter."

    response_body = f"""Hej!

Tack för din förfrågan om {product_query}.

Här är vårt sortiment:

{product_text}

Kontakta oss gärna för offert!

Vänliga hälsningar,
Bengtssons Trävaror"""

    # 3. Skicka svar (om aktiverat)
    if SEND_EMAILS:
        try:
            gmail = get_gmail_client()
            gmail._send_email(from_email, f"Re: {subject}", response_body)
            return f"Försäljningsförfrågan hanterad för {from_email}: {len(matches)} produkter hittades, svar skickat"
        except Exception as e:
            return f"Kunde inte skicka svar: {e}"
    else:
        return f"[DRY-RUN] Försäljningsförfrågan hanterad för {from_email}: {len(matches)} produkter (mail EJ skickat)"


@mcp.tool()
def handle_estimate_email(from_email: str, subject: str, project_description: str) -> str:
    """
    Hanterar en materialberäkningsförfrågan komplett:
    1. Beräknar materialbehov med AI
    2. Formaterar snyggt svar
    3. Skickar svar till kunden

    Args:
        project_description: Beskrivning av projektet (t.ex. "garage 40 kvm")

    Returns:
        Bekräftelse på vad som gjordes
    """
    from core.agents import SalesAgent

    # 1. Beräkna material
    agent = SalesAgent()
    estimated = agent.estimate_materials_json(project_description)

    if not estimated:
        return f"Kunde inte beräkna material för: {project_description}"

    # 2. Beräkna priser och formatera per kategori
    total = 0
    lines = ["Här är vår uppskattning av materialbehov:\n"]

    for category, products in estimated.items():
        # Hantera både ny grupperad struktur och gammal platt struktur
        if isinstance(products, dict):
            lines.append(f"\n📦 {category}:")
            for product, qty in products.items():
                if product in PRODUCTS:
                    price = PRODUCTS[product][0]
                    line_total = price * qty
                    total += line_total
                    name = product.replace('_', ' ')
                    lines.append(f"   • {name}: {qty} st à {price} kr = {line_total} kr")
        else:
            # Fallback för gammal platt struktur
            product, qty = category, products
            if product in PRODUCTS:
                price = PRODUCTS[product][0]
                line_total = price * qty
                total += line_total
                name = product.replace('_', ' ')
                lines.append(f"• {name}: {qty} st à {price} kr = {line_total} kr")

    lines.append(f"\n💰 Uppskattad totalkostnad: {total} kr")
    lines.append("\nVill du att vi tar fram en officiell offert?")

    response_body = f"""Hej!

Tack för din förfrågan.

{chr(10).join(lines)}

Vänliga hälsningar,
Bengtssons Trävaror"""

    # 3. Skicka svar (om aktiverat)
    if SEND_EMAILS:
        try:
            gmail = get_gmail_client()
            gmail._send_email(from_email, f"Re: {subject}", response_body)
            return f"Materialberäkning hanterad för {from_email}: {len(estimated)} produkter beräknade, totalt {total} kr, svar skickat"
        except Exception as e:
            return f"Kunde inte skicka svar: {e}"
    else:
        return f"[DRY-RUN] Materialberäkning hanterad för {from_email}: {len(estimated)} produkter, totalt {total} kr (mail EJ skickat)"


@mcp.tool()
def handle_meeting_email(from_email: str, subject: str, meeting_time: str = None) -> str:
    """
    Hanterar en mötesförfrågan komplett:
    1. Noterar önskad tid (om angiven)
    2. Skickar bekräftelse till kunden

    Args:
        meeting_time: Önskad mötestid (ISO-format) eller None om ej angiven

    Returns:
        Bekräftelse på vad som gjordes
    """
    if meeting_time:
        response_body = f"""Hej!

Tack för din mötesförfrågan.

Vi har noterat önskad tid: {meeting_time}

Vi återkommer med bekräftelse.

Vänliga hälsningar,
Bengtssons Trävaror"""
                        
        result = f"Mötesförfrågan hanterad för {from_email}: Tid noterad ({meeting_time}), bekräftelse skickad"
    else:
        response_body = f"""Hej!

Tack för din mötesförfrågan.

Vänligen ange önskad tid så återkommer vi.

Vänliga hälsningar,
Bengtssons Trävaror"""
                    
        result = f"Mötesförfrågan hanterad för {from_email}: Ingen tid angiven, svar skickat"

    if SEND_EMAILS:
        try:
            gmail = get_gmail_client()
            gmail._send_email(from_email, f"Re: {subject}", response_body)
            return result
        except Exception as e:
            return f"Kunde inte skicka svar: {e}"
    else:
        return f"[DRY-RUN] {result.replace('skickad', '(mail EJ skickat)')}"


@mcp.tool()
def notify_manager(from_email: str, subject: str, body: str, email_type: str) -> str:
    """
    Skickar notifikation till chef om ett högprioriterat ärende.

    Args:
        from_email: Kundens e-postadress
        subject: Ärendeämne
        body: Meddelandetext
        email_type: Typ av ärende (support/sales/estimate/meeting/other)

    Returns:
        Bekräftelse på om notifikation skickades
    """
    if not MANAGER_EMAIL:
        return "[VARNING] MANAGER_EMAIL ej konfigurerad - kunde inte eskalera"

    notification_body = f"""HÖGPRIORITERAT ÄRENDE

Typ: {email_type.upper()}
Från: {from_email}
Ämne: {subject}

--- Kundens meddelande ---
{body}
---

Detta ärende har flaggats som högprioriterat av AI-systemet.
Vänligen granska och vidta lämplig åtgärd.

/ Bengtssons Trävaror - Automatisk notifikation"""

    if SEND_EMAILS:
        try:
            gmail = get_gmail_client()
            gmail._send_email(
                MANAGER_EMAIL,
                f"Hög prioritet: {subject}",
                notification_body
            )
            return f"Eskalering skickad till {MANAGER_EMAIL}"
        except Exception as e:
            return f"Kunde inte skicka eskalering: {e}"
    else:
        return f"[DRY-RUN] Eskalering till {MANAGER_EMAIL} (mail EJ skickat)"


# ==================== MAIN ====================

if __name__ == "__main__":
    mcp.run()
