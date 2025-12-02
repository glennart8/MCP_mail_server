# MCP Mail Server - Bengtssons Trävaror

En MCP-server (Model Context Protocol) för automatisk e-posthantering hos ett fiktivt byggvaruhus.

## Arkitektur

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              MCP-ARKITEKTUR                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────────────┐         ┌─────────────────────────────────┐   │
│   │      MCP-KLIENT         │         │         MCP-SERVER              │   │
│   │     (mcp_client.py)     │         │        (server.py)              │   │
│   │                         │         │                                 │   │
│   │  "Hjärnan" - BESTÄMMER  │  stdio  │  "Händerna" - UTFÖR arbete     │   │
│   │                         │ ◄─────► │                                 │   │
│   │  • AI-klassificering    │   MCP   │  • Hämta mail                   │   │
│   │  • Beslut om åtgärd     │ proto-  │  • Skicka svar                  │   │
│   │  • Anropar rätt tool    │   col   │  • Logga ärenden                │   │
│   │                         │         │  • Beräkna material             │   │
│   └─────────────────────────┘         └─────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Flödesdiagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           MAIL-HANTERINGSFLÖDE                               │
└──────────────────────────────────────────────────────────────────────────────┘

    KLIENT (AI-beslut)                         SERVER (Tool-exekvering)
    ══════════════════                         ═══════════════════════

    ┌─────────────┐
    │   START     │
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐      get_unread_emails()      ┌─────────────────┐
    │ Hämta mail  │ ─────────────────────────────►│ Returnerar JSON │
    └──────┬──────┘                               │ med alla mail   │
           │◄─────────────────────────────────────└─────────────────┘
           │
           ▼
    ┌─────────────────┐
    │  För varje mail │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────────┐
    │  AI KLASSIFICERAR   │  (Gemini 2.0 Flash)
    │                     │
    │  Kategorier:        │
    │  • support          │
    │  • sales            │
    │  • estimate         │
    │  • meeting          │
    │  • other            │
    └─────────┬───────────┘
              │
              ▼
    ┌─────────────────────┐
    │ Anropa rätt handler │
    └─────────┬───────────┘
              │
     ┌────────┴────────┬─────────────────┬─────────────────┐
     ▼                 ▼                 ▼                 ▼
┌─────────┐      ┌─────────┐      ┌─────────────┐   ┌─────────┐
│ support │      │  sales  │      │  estimate   │   │ meeting │
└────┬────┘      └────┬────┘      └──────┬──────┘   └────┬────┘
     │                │                  │               │
     ▼                ▼                  ▼               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SERVER TOOLS                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  handle_support_email()    handle_sales_email()    handle_estimate_email()  │
│  ├─ Logga klagomål        ├─ Sök produkter        ├─ AI beräknar material  │
│  ├─ AI genererar svar     ├─ Formatera svar       ├─ Beräkna priser        │
│  └─ Skicka mail           └─ Skicka mail          └─ Skicka mail           │
│                                                                             │
│  handle_meeting_email()                                                     │
│  ├─ Notera önskad tid                                                       │
│  └─ Skicka bekräftelse                                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
              │
              ▼
    ┌─────────────────┐
    │ Nästa mail...   │
    └─────────────────┘
```

## Filstruktur

```
MCP-Mail-Server/
├── server.py              # MCP-server med tools och resources
├── mcp_client.py          # Autonom klient med AI-klassificering
├── core/
│   ├── __init__.py
│   ├── agents.py          # AI-agenter (ComplaintAgent, SalesAgent)
│   ├── autoresponder.py   # Gmail API-integration
│   ├── conversations.py   # Konversationshistorik per kund
│   ├── products.py        # Produktkatalog
│   └── test_data.py       # Testmail för demonstration
├── conversations.json     # Kundhistorik (ej i repo, GDPR)
├── credentials.json       # Google OAuth (ej i repo)
├── .env                   # API-nycklar (ej i repo)
└── requirements.txt
```

## Tools (server.py)

| Tool | Beskrivning | Input |
|------|-------------|-------|
| `get_unread_emails` | Hämtar alla olästa mail från inkorgen | - |
| `handle_support_email` | Hanterar klagomål: loggar, genererar AI-svar, skickar | `from_email`, `subject`, `body` |
| `handle_sales_email` | Hanterar produktförfrågningar: söker, formaterar, skickar | `from_email`, `subject`, `product_query` |
| `handle_estimate_email` | Hanterar materialberäkningar: AI-beräkning, prissättning, skickar | `from_email`, `subject`, `project_description` |
| `handle_meeting_email` | Hanterar mötesförfrågningar: noterar tid, skickar bekräftelse | `from_email`, `subject`, `meeting_time` (valfri) |

## Resources (server.py)

| Resource | Beskrivning |
|----------|-------------|
| `products://catalog` | Produktkatalog med priser och dimensioner |

## Core-moduler

### agents.py
| Klass | Metod | Beskrivning |
|-------|-------|-------------|
| `BaseAgent` | `run_llm()` | Kör prompt mot Gemini, returnerar text |
| `BaseAgent` | `run_llm_json()` | Kör prompt, returnerar JSON |
| `ComplaintAgent` | `write_response_to_complaint()` | Genererar svar på klagomål (med konversationshistorik) |
| `SalesAgent` | `estimate_materials_json()` | Beräknar materialåtgång för byggprojekt |

### conversations.py
| Funktion | Beskrivning |
|----------|-------------|
| `add_message()` | Sparar ett meddelande i historiken |
| `get_history()` | Hämtar konversationshistorik för en kund |
| `format_history_for_prompt()` | Formaterar historik för AI-prompten |

### autoresponder.py
| Klass | Metod | Beskrivning |
|-------|-------|-------------|
| `AutoResponder` | `_send_email()` | Skickar mail via Gmail API |

### products.py
| Konstant | Beskrivning |
|----------|-------------|
| `PRODUCTS` | Dict med produkter: `{namn: (pris, dimension)}` |

## Installation

```bash
# Klona och installera
cd MCP-Mail-Server
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt

# Konfigurera
cp .env.example .env
# Redigera .env med din GEMINI_API_KEY
```

## Konfiguration

### Miljövariabler (.env)
```
GEMINI_API_KEY=din-api-nyckel
SENDER_EMAIL=din@email.com
USE_GMAIL=false                # true för att läsa från riktig Gmail
SEND_REAL_EMAILS=false         # true för att skicka riktiga mail
```

### Google OAuth (för Gmail-utskick)
1. Skapa projekt i [Google Cloud Console](https://console.cloud.google.com/)
2. Aktivera Gmail API
3. Skapa OAuth 2.0-credentials (Desktop app)
4. Ladda ner `credentials.json` till projektmappen

## Användning

### Kör den autonoma klienten
```bash
# Kör en gång
python mcp_client.py

# Kör kontinuerligt (var 5:e minut)
python mcp_client.py --loop

# Kör kontinuerligt med eget intervall (var 60:e minut)
python mcp_client.py --loop 60
```

Klienten startar MCP-servern automatiskt, hämtar mail, klassificerar och hanterar dem.

### Använd med Claude Desktop
Lägg till i `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "bengtssons-travaror": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "c:/Users/henri/source/repos/Python/MCP-Mail-Server",
      "env": {
        "GEMINI_API_KEY": "din-api-nyckel"
      }
    }
  }
}
```

## MCP-principen

```
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│   KLIENT = AI som BESTÄMMER           SERVER = Tools som GÖR   │
│                                                                │
│   • Klassificering sker i klienten    • Inga AI-beslut         │
│   • Väljer vilken tool att anropa     • Utför instruktioner    │
│   • Styr hela arbetsflödet            • Returnerar resultat    │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

Denna arkitektur följer MCP-standarden där:
- **Servern** exponerar verktyg (tools) och data (resources)
- **Klienten** innehåller AI-logiken som fattar beslut
