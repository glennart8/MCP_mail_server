# MCP Mail Server - Bengtssons Trävaror

En MCP-server (Model Context Protocol) för e-posthantering och affärssystem.

## Funktioner (Tools)

| Tool | Beskrivning |
|------|-------------|
| `get_unread_emails` | Hämtar olästa e-postmeddelanden |
| `create_support_ticket` | Skapar supportärende för klagomål |
| `create_quote` | Genererar och skickar offert |
| `estimate_materials` | Beräknar materialåtgång för byggprojekt |
| `send_estimate_email` | Skickar materialuppskattning till kund |
| `create_calendar_event` | Bokar möte i Google Calendar |
| `send_email` | Skickar e-post via Gmail |
| `search_products` | Söker i produktkatalogen |
| `get_product_price` | Hämtar pris för specifik produkt |
| `check_followups` | Kontrollerar offerter som behöver uppföljning |

## Resurser (Resources)

| Resource | Beskrivning |
|----------|-------------|
| `products://catalog` | Hela produktkatalogen |
| `logs://complaints` | Registrerade klagomål |
| `logs://quotes` | Skickade offerter |

## Installation

```bash
# Klona repot
cd MCP-Mail-Server

# Skapa virtuell miljö
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Installera beroenden
pip install -r requirements.txt

# Kopiera och konfigurera miljövariabler
copy .env.example .env
# Redigera .env med dina API-nycklar
```

## Google API Setup

1. Gå till [Google Cloud Console](https://console.cloud.google.com/)
2. Skapa ett projekt
3. Aktivera Gmail API och Google Calendar API
4. Skapa OAuth 2.0-credentials (Desktop app)
5. Ladda ner `credentials.json` och placera i projektmappen

## Konfigurera i Claude Desktop

Lägg till i `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "bengtssons-travaror": {
      "command": "python",
      "args": ["c:/Users/henri/source/repos/MCP-Mail-Server/server.py"],
      "env": {
        "GEMINI_API_KEY": "din-api-nyckel"
      }
    }
  }
}
```

## Användning

Starta servern direkt:
```bash
python server.py
```

Eller använd via en MCP-klient som Claude Desktop.

## Exempel

### Klassificera och hantera mail
```
> Hämta nya mail och klassificera dem
> Skapa en offert för kund@example.com med 10 st plywood_12mm och 5 st regel_45x95_3m
```

### Materialberäkning
```
> Beräkna materialåtgång för en altan på 30 kvm
> Skicka uppskattningen till kund@example.com
```

### Produktsökning
```
> Sök efter produkter som innehåller "isolering"
> Vad kostar plywood_15mm?
```

## Struktur

```
MCP-Mail-Server/
├── server.py           # MCP-server med alla tools
├── agents.py           # AI-agenter (Gemini)
├── products.py         # Produktkatalog
├── sales.py            # Försäljningssystem
├── complaints.py       # Klagomålshantering
├── mail.py             # E-postklient
├── autoresponder.py    # Gmail API-integration
├── calendar_handler.py # Google Calendar-integration
├── logs/               # Loggfiler
├── requirements.txt
├── .env.example
└── README.md
```
