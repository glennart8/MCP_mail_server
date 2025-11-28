"""Försäljningssystem för offerter och materialberäkningar."""

import json
from datetime import datetime

from .agents import SalesAgent
from .autoresponder import AutoResponder
from .products import PRODUCTS


class SalesSystem:
    """Hanterar offerter, beställningar och materialberäkningar."""

    def __init__(self):
        self.products = PRODUCTS
        self._auto = None
        self._sales_agent = None

    @property
    def auto(self):
        if self._auto is None:
            self._auto = AutoResponder()
        return self._auto

    @property
    def sales_agent(self):
        if self._sales_agent is None:
            self._sales_agent = SalesAgent()
        return self._sales_agent

    def calculate_total(self, order: dict) -> int:
        """Beräknar totalpris för en order."""
        total = 0
        for product, qty in order.items():
            if product in self.products:
                price = self.products[product][0]
                total += price * qty
        return total

    def create_quote(self, email: dict):
        """Skapar och skickar en offert baserad på ett kundmail."""
        # Låt LLM extrahera produkter från mailet
        order_details = self.sales_agent.extract_order_from_email(email)

        print("LLM-svar:", order_details)

        found_items = order_details["found"]
        not_found_items = order_details["not_found"]
        suggestions = order_details["suggestions"]

        # Lägg till föreslagna alternativ
        for missing_product, suggested_product in suggestions.items():
            qty = not_found_items.get(missing_product, 1)
            if suggested_product in self.products:
                found_items[suggested_product] = found_items.get(suggested_product, 0) + qty
                print(f"Lägger till föreslaget alternativ: {suggested_product} ({qty} st)")

        # Beräkna totalpris
        total_price = self.calculate_total(found_items)

        # Skapa offerttext
        quote_lines = []
        for product, qty in found_items.items():
            price = self.products[product][0]
            quote_lines.append(f"{product}: {qty} st x {price} kr")

        # Lägg till meddelanden för saknade produkter
        for product in not_found_items:
            suggestion_text = suggestions.get(product)
            if suggestion_text:
                quote_lines.append(
                    f"\nOBS: Vi kunde inte hitta {product}, "
                    f"men föreslår {suggestion_text} istället."
                )
            else:
                quote_lines.append(
                    f"\nOBS: Vi kunde tyvärr inte hitta {product} i sortimentet."
                )

        body = (
            "Hej!\n\n"
            "Här är offerten du efterfrågade:\n\n"
            f"{chr(10).join(quote_lines)}\n\n"
            f"Totalpris: {total_price} SEK\n\n"
            "Vill du lägga en order?\n\n"
            "Vänliga hälsningar,\n"
            "Bengtssons trävaror"
        )

        # Skicka mailet
        subject = f"Offert: {email['subject']}"
        self.auto._send_email(email['from'], subject, body)
        print(f"Offert skickad till {email['from']}")

        self.save_sent_quote(email, found_items)

    def save_sent_quote(self, email: dict, products: dict):
        """Sparar en skickad offert för uppföljning."""
        quote_data = {
            "customer": email["from"],
            "subject": email["subject"],
            "products": products,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "followed_up": False
        }
        with open("logs/sent_quotes.json", "a", encoding="utf-8") as f:
            f.write(json.dumps(quote_data, ensure_ascii=False) + "\n")

        print("Offert sparad")

    def check_for_followups(self):
        """Kontrollerar och skickar uppföljningsmail för gamla offerter."""
        try:
            with open("logs/sent_quotes.json", "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            return

        for line in lines:
            quote = json.loads(line)
            sent_date = datetime.strptime(quote["date"], "%Y-%m-%d %H:%M")
            if not quote["followed_up"] and (datetime.now() - sent_date).days >= 1:
                self.send_followup(quote)
                quote["followed_up"] = True

    def send_followup(self, quote: dict):
        """Skickar uppföljningsmail för en offert."""
        customer = quote["customer"]
        products = ", ".join(quote["products"].keys())
        subject = "Uppföljning på din offert"

        body = (
            f"Hej!\n\n"
            f"Vi skickade en offert på {products} häromdagen. "
            f"Vill du att vi lägger in en beställning åt dig eller har du några frågor?\n\n"
            f"Vänliga hälsningar,\n"
            f"Bengtssons trävaror"
        )

        self.auto._send_email(customer, subject, body)
        print(f"Uppföljningsmail skickat till {customer}")

    def estimate_materials_for_email(self, email: dict) -> dict | None:
        """Beräknar materialåtgång baserat på ett kundmail."""
        description = email["body"]
        estimated_materials = self.sales_agent.estimate_materials_json(description)

        if not estimated_materials:
            print("Kunde inte beräkna materialåtgång.")
            return None

        return estimated_materials

    def create_estimate_email(self, email: dict):
        """Skapar och skickar ett mail med materialuppskattning."""
        estimated_materials = self.estimate_materials_for_email(email)
        if not estimated_materials:
            return

        # Skapa offerttext
        quote_lines = [
            f"{prod}: {qty} st x {self.products[prod][0]} kr"
            for prod, qty in estimated_materials.items()
            if prod in self.products
        ]

        total_price = sum(
            self.products[prod][0] * qty
            for prod, qty in estimated_materials.items()
            if prod in self.products
        )

        body = (
            f"Hej!\n\n"
            f"Utifrån din beskrivning har vi uppskattat följande materialåtgång:\n\n"
            f"{chr(10).join(quote_lines)}\n\n"
            f"Uppskattat totalpris: {total_price} kr\n\n"
            "Vill du att vi tar fram en officiell offert baserat på dessa mängder?\n\n"
            "Vänliga hälsningar,\n"
            "Bengtssons trävaror"
        )

        subject = f"Uppskattad materialåtgång: {email['subject']}"
        self.auto._send_email(email['from'], subject, body)
        print(f"Materialuppskattning skickad till {email['from']}")
