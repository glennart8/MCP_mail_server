"""
MCP Server för Bengtssons Trävaror - E-posthantering och affärssystem.

Denna server exponerar verktyg för:
- Hämta e-post
- Skapa supportärenden (klagomål)
- Generera offerter
- Boka möten i Google Calendar
- Beräkna materialåtgång för byggprojekt
- Skicka e-post
"""

import json
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Importera affärslogik från core/
from core.complaints import ComplaintsSystem
from core.sales import SalesSystem
from core.autoresponder import AutoResponder
from core.calendar_handler import CalendarHandler
from core.products import PRODUCTS
from core.mail import EmailClient

# Skapa MCP-server
mcp = FastMCP("bengtssons-travaror")

# Initiera system
complaints_system = ComplaintsSystem()
sales_system = SalesSystem()
email_client = EmailClient()

# Lazy-loading för Google API (kräver autentisering)
_autoresponder = None
_calendar = None

def get_autoresponder():
    global _autoresponder
    if _autoresponder is None:
        _autoresponder = AutoResponder()
    return _autoresponder

def get_calendar():
    global _calendar
    if _calendar is None:
        _calendar = CalendarHandler()
    return _calendar


# ==================== RESOURCES ====================

@mcp.resource("products://catalog")
def get_product_catalog() -> str:
    """Returnerar hela produktkatalogen med priser och dimensioner."""
    catalog_lines = []
    for name, (price, dimension) in PRODUCTS.items():
        dim_str = f"{dimension} m/kvm" if dimension else "styck"
        catalog_lines.append(f"{name}: {price} kr ({dim_str})")
    return "\n".join(catalog_lines)


@mcp.resource("logs://complaints")
def get_complaints_log() -> str:
    """Returnerar alla registrerade klagomål."""
    return json.dumps(complaints_system.complaints, ensure_ascii=False, indent=2)


@mcp.resource("logs://quotes")
def get_quotes_log() -> str:
    """Returnerar alla skickade offerter."""
    try:
        with open("logs/sent_quotes.json", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "[]"


# ==================== TOOLS ====================

@mcp.tool()
def get_unread_emails() -> str:
    """
    Hämtar olästa e-postmeddelanden från inkorgen.

    Returnerar en lista med e-post i JSON-format med fälten:
    - from: avsändarens e-postadress
    - subject: ämnesrad
    - body: meddelandetext
    """
    emails = email_client.get_new_emails()
    if not emails:
        return json.dumps({"message": "Inga nya mail"}, ensure_ascii=False)
    return json.dumps(emails, ensure_ascii=False, indent=2)


@mcp.tool()
def create_support_ticket(from_email: str, subject: str, body: str, send_response: bool = True) -> str:
    """
    Skapar ett supportärende för ett kundklagomål.

    Returns:
        Bekräftelse på att ärendet skapats
    """
    email = {"from": from_email, "subject": subject, "body": body}
    complaints_system.log_complaint(email)

    result = f"Supportärende skapat för {from_email}: {subject}"

    if send_response:
        try:
            auto = get_autoresponder()
            auto.create_auto_response_complaint(email, to=from_email)
            result += f"\nAutomatiskt svar skickat till {from_email}."
        except Exception as e:
            result += f"\nKunde inte skicka autosvar: {e}"

    return result


@mcp.tool()
def create_quote(customer_email: str, subject: str, products: dict[str, int]) -> str:
    """
    Skapar och skickar en offert till kunden.

    Returns:
        Offertdetaljer och bekräftelse
    """
    # Beräkna totalpris
    quote_lines = []
    total_price = 0
    unknown_products = []

    for product, qty in products.items():
        if product in PRODUCTS:
            price = PRODUCTS[product][0]  # Första värdet är priset
            line_total = price * qty
            total_price += line_total
            quote_lines.append(f"{product}: {qty} st x {price} kr = {line_total} kr")
        else:
            unknown_products.append(product)

    # Bygg offerttext
    body = (
        "Hej!\n\n"
        "Här är offerten du efterfrågade:\n\n"
        f"{chr(10).join(quote_lines)}\n\n"
        f"Totalpris: {total_price} SEK\n\n"
    )

    if unknown_products:
        body += f"OBS: Följande produkter kunde inte hittas: {', '.join(unknown_products)}\n\n"

    body += (
        "Vill du lägga en order?\n\n"
        "Vänliga hälsningar,\n"
        "Bengtssons trävaror"
    )

    # Skicka mail
    try:
        auto = get_autoresponder()
        auto._send_email(customer_email, f"Offert: {subject}", body)

        # Spara offert
        sales_system.save_sent_quote(
            {"from": customer_email, "subject": subject},
            products
        )

        return f"Offert skickad till {customer_email}\n\nInnehåll:\n{body}"
    except Exception as e:
        return f"Kunde inte skicka offert: {e}\n\nOffertinnehåll:\n{body}"


@mcp.tool()
def estimate_materials(project_description: str) -> str:
    """
    Beräknar uppskattad materialåtgång för ett byggprojekt.

    Använder AI för att analysera projektbeskrivningen och returnerar
    en lista med rekommenderade produkter och mängder.

    Args:
        project_description: Beskrivning av byggprojektet (t.ex. "altan 30 kvm" eller "garage 40 kvm")

    Returns:
        JSON med produkter och antal, samt uppskattad totalkostnad
    """
    from core.agents import SalesAgent

    agent = SalesAgent()
    estimated = agent.estimate_materials_json(project_description)

    if not estimated:
        return json.dumps({"error": "Kunde inte beräkna materialåtgång"}, ensure_ascii=False)

    # Beräkna totalpris
    total = 0
    result_lines = []
    for product, qty in estimated.items():
        if product in PRODUCTS:
            price = PRODUCTS[product][0]
            line_total = price * qty
            total += line_total
            result_lines.append({
                "product": product,
                "quantity": qty,
                "unit_price": price,
                "line_total": line_total
            })

    return json.dumps({
        "project": project_description,
        "materials": result_lines,
        "total_estimated_price": total
    }, ensure_ascii=False, indent=2)


@mcp.tool()
def send_estimate_email(
    customer_email: str, subject: str, project_description: str) -> str:
    """
    Beräknar materialåtgång och skickar uppskattningen till kunden via e-post.

    Returns:
        Bekräftelse på skickat mail med innehåll
    """
    email = {
        "from": customer_email,
        "subject": subject,
        "body": project_description
    }

    try:
        sales_system.create_estimate_email(email)
        return f"Materialuppskattning skickad till {customer_email}"
    except Exception as e:
        return f"Fel vid skickande: {e}"


@mcp.tool()
def create_calendar_event(
    title: str,
    description: str,
    start_time: str,
    duration_minutes: int = 60
) -> str:
    """
    Skapar ett möte i Google Calendar.

    Returns:
        Bekräftelse med länk till kalenderhändelsen
    """
    try:
        calendar = get_calendar()
        start = datetime.fromisoformat(start_time)
        calendar.create_event(title, description, start, duration_minutes)
        return f"Möte '{title}' skapat för {start_time}"
    except Exception as e:
        return f"Kunde inte skapa möte: {e}"


@mcp.tool()
def send_email( to: str, subject: str, body: str) -> str:
    """
    Skickar ett e-postmeddelande via Gmail.

    Returns:
        Bekräftelse på skickat mail
    """
    try:
        auto = get_autoresponder()
        auto._send_email(to, subject, body)
        return f"Mail skickat till {to}"
    except Exception as e:
        return f"Kunde inte skicka mail: {e}"


@mcp.tool()
def search_products(query: str) -> str:
    """
    Söker efter produkter i katalogen.

    Args:
        query: Sökterm (t.ex. "plywood", "regel", "isolering")

    Returns:
        Lista med matchande produkter och priser
    """
    query_lower = query.lower()
    matches = []

    for name, (price, dimension) in PRODUCTS.items():
        if query_lower in name.lower():
            dim_str = f"{dimension} m/kvm" if dimension else "styck"
            matches.append({
                "name": name,
                "price": price,
                "dimension": dim_str
            })

    if not matches:
        return json.dumps({"message": f"Inga produkter hittades för '{query}'"}, ensure_ascii=False)

    return json.dumps(matches, ensure_ascii=False, indent=2)


@mcp.tool()
def check_followups() -> str:
    """
    Kontrollerar om det finns offerter som behöver uppföljning.

    Returnerar lista med offerter som skickades för mer än 1 dag sedan
    och som ännu inte följts upp.
    """
    try:
        sales_system.check_for_followups()
        return "Uppföljningskontroll genomförd"
    except Exception as e:
        return f"Fel vid uppföljningskontroll: {e}"


@mcp.tool()
def get_product_price(product_name: str) -> str:
    """
    Hämtar pris och information för en specifik produkt.

    Returns:
        Produktinformation med pris
    """
    if product_name in PRODUCTS:
        price, dimension = PRODUCTS[product_name]
        dim_str = f"{dimension} m/kvm" if dimension else "styck"
        return json.dumps({
            "name": product_name,
            "price": price,
            "dimension": dim_str
        }, ensure_ascii=False)

    # Försök hitta liknande produkter
    suggestions = [name for name in PRODUCTS.keys() if product_name.lower() in name.lower()]
    return json.dumps({
        "error": f"Produkten '{product_name}' finns inte",
        "suggestions": suggestions[:5]
    }, ensure_ascii=False)


# ==================== PROMPTS ====================

@mcp.prompt()
def classify_email(email_from: str, email_subject: str, email_body: str) -> str:
    """Prompt för att klassificera ett inkommande mail."""
    return f"""Du är en kontorsassistent för Bengtssons Trävaror. Analysera följande e-post och klassificera den.

E-post:
Från: {email_from}
Ämne: {email_subject}
Meddelande: {email_body}

Klassificera mailet som EN av följande:
- "support" - klagomål eller reklamation
- "sales" - offertförfrågan eller köp
- "meeting" - mötesbokning
- "estimate" - förfrågan om materialberäkning för byggprojekt
- "other" - övrigt

Svara med vilken kategori och förklara kort varför. Om det är "sales", lista vilka produkter kunden är intresserad av. 
Om det är "meeting", extrahera datum och tid om det anges."""


@mcp.prompt()
def draft_quote_response(customer_name: str, products: str, total: str) -> str:
    """Prompt för att skriva ett offertmail."""
    return f"""Skriv ett professionellt och vänligt offertmail till {customer_name}.

Produkter och priser:
{products}

Totalt: {total} SEK

Inkludera:
1. Hälsning
2. Offertdetaljer
3. Giltighetstid (30 dagar)
4. Kontaktinformation
5. Avslutande hälsning från Bengtssons Trävaror"""


# ==================== MAIN ====================

if __name__ == "__main__":
    mcp.run()
