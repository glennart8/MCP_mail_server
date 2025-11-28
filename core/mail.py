"""E-postklient med fake inbox för demonstration.

Innehåller påhittade testmail för att demonstrera MCP-serverns funktionalitet.
Alla svar skickas till avsändaren (from-fältet).
"""

# Testinkorg med varierade mail (alla från henrikpilback@gmail.com för testning)
INBOX = [
    {
        "from": "henrikpilback@gmail.com",
        "subject": "Offertförfrågan - Altanbygge",
        "body": """Hej!

Jag planerar att bygga en altan på ca 25 kvm och undrar om ni kan ge mig en offert.

Behöver ungefär:
- Altangolv (bräder)
- Reglar för stommen
- Skruv och beslag

Kan ni skicka en prisuppskattning?

Mvh,
Anna Svensson"""
    },
    {
        "from": "henrikpilback@gmail.com",
        "subject": "Klagomål - Fel leverans",
        "body": """Hej,

Jag beställde 50 st bräda 22x145 förra veckan men fick bara 40 st levererade.
Dessutom var 5 av brädorna spruckna.

Ordernummer: 2024-1234

Jag vill ha ersättning för de saknade och skadade brädorna.

Erik Johansson"""
    },
    {
        "from": "henrikpilback@gmail.com",
        "subject": "Boka möte - Stororder",
        "body": """Hej!

Vi planerar ett större byggprojekt och skulle vilja boka ett möte.
Kan vi ses på fredag kl 14:00?

Med vänlig hälsning,
Maria Lindqvist
Lindqvist Bygg AB"""
    },
    {
        "from": "henrikpilback@gmail.com",
        "subject": "Materialberäkning garage 40kvm",
        "body": """Hej Bengtssons!

Kan ni göra en uppskattning av materialbehov för ett garage på 40 kvm?

Garaget ska ha:
- Regelstomme
- Plywoodskivor på väggarna
- Mineralullsisolering
- Takpannor

Tack!
Lisa Berg"""
    },
    {
        "from": "henrikpilback@gmail.com",
        "subject": "Prisförfrågan plywood",
        "body": """Tjena!

Vad kostar plywood 12mm hos er? Behöver 20 skivor.
Har ni OSB-skivor också?

/Anders"""
    },
]


class EmailClient:
    """Enkel e-postklient som hämtar mail från inkorgen."""

    def __init__(self):
        self.inbox = INBOX.copy()

    def get_new_emails(self) -> list:
        """Hämtar nya e-postmeddelanden (tar bort dem från inkorgen)."""
        if self.inbox:
            return [self.inbox.pop(0)]
        return []

    def peek_emails(self) -> list:
        """Tittar på inkorgen utan att ta bort mail."""
        return self.inbox.copy()

    def add_test_email(self, from_addr: str, subject: str, body: str):
        """Lägger till ett testmail i inkorgen."""
        self.inbox.append({
            "from": from_addr,
            "subject": subject,
            "body": body
        })
