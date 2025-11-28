"""Test-agent som hanterar mail från fake inbox.

Kör: python agent_runner.py
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

from core.mail import EmailClient
from core.complaints import ComplaintsSystem
from core.products import PRODUCTS
from core.agents import SupervisorAgent, SalesAgent, ComplaintAgent

# Sätt till True för att skicka riktiga mail
SEND_REAL_EMAILS = False

def main():
    email_client = EmailClient()
    complaints = ComplaintsSystem()
    supervisor = SupervisorAgent()
    sales_agent = SalesAgent()
    complaint_agent = ComplaintAgent()

    autoresponder = None
    if SEND_REAL_EMAILS:
        from core.autoresponder import AutoResponder
        autoresponder = AutoResponder()

    emails = email_client.peek_emails()
    print(f"\n=== MAIL AGENT - {len(emails)} mail ===\n")

    for i, email in enumerate(emails, 1):
        print(f"[{i}] {email['subject']}")
        print(f"    Från: {email['from']}")

        # Klassificera
        decision, _, meeting_time = supervisor.decide(email)
        print(f"    → Typ: {decision.upper()}")

        # Hantera baserat på typ
        if decision == "support":
            complaints.log_complaint(email)
            response = complaint_agent.write_response_to_complaint(email)
            print(f"    → Svar genererat ({len(response)} tecken)")
            if autoresponder:
                autoresponder._send_email(email['from'], f"Svar: {email['subject']}", response)
                print(f"    → Mail skickat")

        elif decision == "sales":
            order = sales_agent.extract_order_from_email(email)
            found = order.get('found', {})
            if found:
                total = sum(PRODUCTS[p][0] * q for p, q in found.items() if p in PRODUCTS)
                print(f"    → Offert: {list(found.keys())} = {total} kr")

        elif decision == "estimate":
            materials = sales_agent.estimate_materials_json(email['body'])
            if materials:
                total = sum(PRODUCTS[p][0] * q for p, q in materials.items() if p in PRODUCTS)
                print(f"    → Materialkostnad: {total} kr")

        elif decision == "meeting":
            print(f"    → Mötestid: {meeting_time or 'Ej angiven'}")

        print()

    print(f"=== Klart! Klagomål registrerade: {len(complaints.complaints)} ===")


if __name__ == "__main__":
    main()
