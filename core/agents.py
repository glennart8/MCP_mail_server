"""AI-agenter för e-posthantering med Gemini LLM."""

import json
import os
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

from .products import PRODUCTS

load_dotenv()


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


class ComplaintAgent(BaseAgent):
    """Agent som genererar svar på kundklagomål."""

    def write_response_to_complaint(self, email: dict) -> str:
        """Genererar ett svar på ett kundklagomål."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
    """Agent som beräknar materialåtgång för byggprojekt."""

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
