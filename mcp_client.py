"""Autonom MCP-klient som hanterar alla mail automatiskt.

Kör: python mcp_client.py

Agenten:
1. Ansluter till MCP-servern
2. Hämtar alla mail
3. Klassificerar och hanterar varje mail
4. Avslutar
"""

import sys
import io
import os
import json
import asyncio

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from dotenv import load_dotenv
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()


class AutoAgent:
    """Autonom agent som hanterar mail via MCP."""

    def __init__(self, session):
        self.session = session
        self.tools = []

        self.llm = OpenAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

    async def call_tool(self, name: str, arguments: dict = None) -> str:
        """Anropar ett MCP-verktyg."""
        result = await self.session.call_tool(name, arguments or {})
        if result.content:
            for content in result.content:
                if hasattr(content, 'text'):
                    return content.text
        return str(result)

    def classify_email(self, email: dict) -> tuple[str, dict]:
        """Klassificerar ett mail och returnerar (typ, extra_data)."""
        prompt = f"""Klassificera detta mail. Svara ENDAST med JSON.

Mail:
Från: {email['from']}
Ämne: {email['subject']}
Innehåll: {email['body']}

Svara med:
{{
    "type": "support" | "sales" | "estimate" | "meeting" | "other",
    "products": {{"produktnamn": antal}},  // om sales
    "project_description": "...",  // om estimate
    "meeting_time": "YYYY-MM-DDTHH:MM:SS"  // om meeting
}}"""

        response = self.llm.chat.completions.create(
            model="gemini-2.0-flash",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.replace("```json", "").replace("```", "").strip()

        try:
            data = json.loads(raw)
            return data.get("type", "other"), data
        except:
            return "other", {}

    async def handle_support(self, email: dict):
        """Skapar supportärende."""
        result = await self.call_tool("create_support_ticket", {
            "from_email": email['from'],
            "subject": email['subject'],
            "body": email['body'],
            "send_response": False  # Skicka inte mail i testläge
        })
        print(f"    → Supportärende skapat")
        return result

    async def handle_sales(self, email: dict, data: dict):
        """Skapar offert."""
        products = data.get("products", {})
        if not products:
            print(f"    → Inga produkter identifierade")
            return

        result = await self.call_tool("search_products", {"query": list(products.keys())[0]})
        print(f"    → Produktsökning genomförd")
        return result

    async def handle_estimate(self, email: dict, data: dict):
        """Beräknar material."""
        description = data.get("project_description", email['body'])
        result = await self.call_tool("estimate_materials", {
            "project_description": description
        })

        # Parsa resultatet
        try:
            estimate = json.loads(result)
            total = estimate.get("total_estimated_price", 0)
            materials = estimate.get("materials", [])
            print(f"    → Material beräknat: {len(materials)} produkter, {total} kr")
        except:
            print(f"    → Materialberäkning klar")

        return result

    async def handle_meeting(self, email: dict, data: dict):
        """Hanterar mötesbokning."""
        meeting_time = data.get("meeting_time")
        if meeting_time:
            print(f"    → Mötestid identifierad: {meeting_time}")
        else:
            print(f"    → Ingen mötestid angiven")
        return None

    async def process_email(self, email: dict, index: int):
        """Bearbetar ett mail."""
        print(f"\n[{index}] {email['subject']}")
        print(f"    Från: {email['from']}")

        # Klassificera
        mail_type, data = self.classify_email(email)
        print(f"    → Typ: {mail_type.upper()}")

        # Hantera baserat på typ
        if mail_type == "support":
            await self.handle_support(email)
        elif mail_type == "sales":
            await self.handle_sales(email, data)
        elif mail_type == "estimate":
            await self.handle_estimate(email, data)
        elif mail_type == "meeting":
            await self.handle_meeting(email, data)
        else:
            print(f"    → Kräver manuell hantering")

    async def run(self):
        """Kör agenten."""
        print("\n" + "="*60)
        print("  AUTONOM MCP MAIL-AGENT")
        print("="*60)

        # Hämta mail via MCP
        print("\nHämtar mail...")
        result = await self.call_tool("get_unread_emails")

        try:
            emails = json.loads(result)
            if isinstance(emails, dict) and "message" in emails:
                print("Inga mail att hantera.")
                return
            if not isinstance(emails, list):
                emails = [emails]
        except:
            print(f"Kunde inte läsa mail: {result}")
            return

        print(f"Hittade {len(emails)} mail")

        # Bearbeta varje mail
        for i, email in enumerate(emails, 1):
            await self.process_email(email, i)

        print("\n" + "="*60)
        print(f"  KLART! Hanterade {len(emails)} mail")
        print("="*60 + "\n")


async def main():
    """Startar den autonoma agenten."""
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Hämta verktyg
            tools_response = await session.list_tools()
            print(f"MCP-server ansluten ({len(tools_response.tools)} verktyg)")

            # Kör agenten
            agent = AutoAgent(session)
            agent.tools = tools_response.tools
            await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
