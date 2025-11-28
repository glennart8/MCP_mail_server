"""AI-agenter för e-posthantering med Gemini LLM."""

import json
import os
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

from .products import PRODUCTS

load_dotenv()

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class BaseAgent:
    """Basklass för AI-agenter med gemensam LLM-funktionalitet."""

    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

    def run_llm(self, prompt: str, temperature: float = 0.5) -> str:
        """Kör ett prompt mot LLM och returnerar textsvaret."""
        response = self.client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )

        raw = response.choices[0].message.content.strip()

        # Ta bort markdown-kodblock om de finns
        if raw.startswith("```"):
            raw = raw.replace("```json", "").replace("```", "").strip()

        return raw

    def run_llm_json(self, prompt: str, temperature: float = 0.3) -> dict | None:
        """Kör ett prompt som ska returnera JSON."""
        raw = self.run_llm(prompt, temperature=temperature)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            print("AI-svaret gick inte att tolka:", raw)
            return None


class SupervisorAgent(BaseAgent):
    """Agent som klassificerar inkommande e-post."""

    def decide(self, email: dict) -> tuple[str, str | None, str | None]:
        """
        Klassificerar ett e-postmeddelande.

        Returns:
            Tuple med (decision, product, meeting_time)
        """
        prompt = f"""
        Du är en kontorsassistent. Läs följande e-post och bestäm vilken kategori den tillhör.

        "support" - hanterar klagomål
        "sales" - hanterar offerter och köp
        "meeting" - hanterar möten
        "estimate" - hanterar uppskattning av virkesåtgång för byggprojekt
        "other" - övriga ärenden som ej kan klassificeras enligt ovan

        E-post:
        Avsändare: {email['from']}
        Ämne: {email['subject']}
        Meddelande: {email['body']}

        Välj EN kategori och svara ENBART med JSON:
        {{
            "decision": "support" | "sales" | "meeting" | "estimate" | "other",
            "reason": "Kort förklaring varför",
            "product": "T.ex. 'plywood'",
            "meeting_time": "YYYY-MM-DDTHH:MM:SS"
        }}

        Om du väljer "sales", skicka med produkten som kunden vill köpa också.

        Om du väljer "meeting":
            Extrahera datum och tid för mötet i ISO-format (YYYY-MM-DDTHH:MM:SS).
        """

        data = self.run_llm_json(prompt)
        if not data:
            return "other", None, None
        return data.get("decision", "other"), data.get("product"), data.get("meeting_time")


class ComplaintAgent(BaseAgent):
    """Agent som hanterar kundklagomål."""

    def write_response_to_complaint(self, email: dict) -> str:
        """Genererar ett svar på ett kundklagomål."""
        prompt = f"""
        Du är en kontorsassistent som besvarar klagomål via mail.
        Läs följande mail och skapa ett anpassat, trevligt och kort svar.

        Mail:
        Från: {email['from']}
        Ämne: {email['subject']}
        Meddelande: {email['body']}

        Innehåll:
        - Bekräftelse på emottagande av mail och vad klagomålet avser
        - En försäkran om att detta ska tas vidare och att vi ber att få återkomma

        Skriv: Detta mail skickades: {now}

        Avsluta med att önska en fortsatt trevlig dag/kväll.
        Med vänliga hälsningar,

        [Kontorsassistenten]
        Bengtssons Trävaror
        """

        return self.run_llm(prompt)


class SalesAgent(BaseAgent):
    """Agent som hanterar försäljning och materialberäkningar."""

    def write_response_to_order(self, email: dict) -> str:
        """Genererar ett kvitto/bekräftelse på en beställning."""
        prompt = f"""
        Du är en vänlig kontorsassistent som skriver ett kvitto/bekräftelse på ett köp.
        Läs följande kundmail:

        Från: {email['from']}
        Ämne: {email['subject']}
        Meddelande: {email['body']}

        Skapa ett kort, professionellt och trevligt svar som innehåller:
        1. Bekräftelse på att kundens beställning har mottagits
        2. Specificera vad kunden önskar köpa (om det framgår av mailet)
        3. Tiden då kvittot skickas: {now}
        4. Avsluta med en vänlig hälsning och önska en fortsatt trevlig dag/kväll

        Skriv svaret på ett sätt som kan skickas direkt till kunden.
        """

        return self.run_llm(prompt)

    def extract_order_from_email(self, email: dict) -> dict:
        """Extraherar produkter och antal från ett kundmail."""
        prompt = f"""
        Du är en byggvaruexpert som hjälper till att tolka kundbeställningar.
        Läs följande kundmail och returnera en JSON med antal per produkt.
        Använd dig av det som finns i sortimentet: {list(PRODUCTS.keys())}

        Om något inte finns i sortimentet, inkludera det under 'not_found',
        och ge ett likvärdigt produktnamn under 'suggestions' kopplat till den saknade produkten.

        Mail:
        {email['body']}

        Svara ENBART med JSON, t.ex.:
        {{
            "found": {{"plywood_12mm": 2, "bräda_22x145_3m": 5}},
            "not_found": {{"isolering_glasull": 1}},
            "suggestions": {{"isolering_glasull": "isolering_mineralull_95mm"}}
        }}
        """

        raw = self.run_llm(prompt)
        try:
            data = json.loads(raw)
            return {
                "found": data.get("found", {}),
                "not_found": data.get("not_found", {}),
                "suggestions": data.get("suggestions", {})
            }
        except json.JSONDecodeError:
            print("Kunde inte tolka LLM-svar:", raw)
            return {"found": {}, "not_found": {}, "suggestions": {}}

    def estimate_materials_json(self, description: str) -> dict | None:
        """Beräknar materialåtgång för ett byggprojekt."""
        prompt = f"""
        Du är en byggnadsteknisk assistent. Läs följande beskrivning av ett byggprojekt
        och uppskatta materialåtgången baserat på standardbyggteknik i Sverige.

        Beskrivning: {description}

        Använd produktsortimentet: {list(PRODUCTS.keys())}

        Följ dessa riktlinjer:
        - Ytterväggar: regel_45x145 cc600 + bräda_22x145 panel
        - Plywood: 1 skiva per 1.2 m² väggyta
        - Isolering: väggyta per förpackning enligt sortimentet
        - Undertak: råspontlucka enligt sortimentet
        - Inkludera endast produkter som behövs

        **Viktigt:** Returnera endast ett JSON-objekt med format:
        Exempel:
        {{
            "regel_45x145_3m": 20,
            "bräda_22x145_3m": 50,
            "plywood_12mm": 10,
            "isolering_mineralull_145mm": 5,
            "råspontlucka_21x95": 15
        }}

        Inga förklaringar, inga listor, inga kommentarer, endast JSON.
        """
        return self.run_llm_json(prompt)
