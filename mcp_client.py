"""Autonom MCP-klient som hanterar alla mail automatiskt.

Kör: python mcp_client.py              (en gång)
     python mcp_client.py --loop       (kontinuerligt, var 5:e minut)
     python mcp_client.py --loop 60    (kontinuerligt, var 60:e minut)

Arkitektur (enligt MCP-principerna):
- KLIENTEN (denna fil) = AI som bestämmer vad som ska göras
- SERVERN (server.py) = Tools som utför arbete

Klienten:
1. Ansluter till MCP-servern
2. Hämtar alla mail (via tool)
3. AI:n klassificerar varje mail (LOKALT i klienten)
4. Anropar rätt handler (via tool)
5. Avslutar (eller väntar och upprepar om --loop)
"""

import sys
import io
import os
import json
import asyncio
import argparse
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from dotenv import load_dotenv
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

# Miljövariabler laddas från .env och ärvs av servern
# USE_GMAIL=true för att läsa från riktig Gmail
# SEND_REAL_EMAILS=true för att skicka riktiga svar
print(f"USE_GMAIL={os.getenv('USE_GMAIL', 'false')}")
print(f"SEND_REAL_EMAILS={os.getenv('SEND_REAL_EMAILS', 'false')}")


class MailAgent:
    """Agent som använder AI för att klassificera mail och MCP-tools för att hantera dem."""

    def __init__(self, session):
        self.session = session
        # AI-modellen som är "hjärnan" i klienten
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
        prompt = f"""Klassificera detta mail. Svara ENDAST med JSON.

                Mail:
                Från: {email['from']}
                Ämne: {email['subject']}
                Innehåll: {email['body']}

                Svara med:
                {{
                    "type": "support" | "sales" | "estimate" | "meeting" | "other",
                    "product": "produktnamn om sales",
                    "project_description": "beskrivning om estimate",
                    "meeting_time": "YYYY-MM-DDTHH:MM:SS om meeting"
                }}

                Kategorier:
                - support: Klagomål, reklamationer, problem
                - sales: Frågor om produkter, priser, vill köpa något
                - estimate: Vill ha materialberäkning för byggprojekt
                - meeting: Vill boka möte
                - other: Övrigt"""

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


    async def process_email(self, email: dict, index: int):
        """Bearbetar ett mail: AI klassificerar, sedan anropas rätt tool."""
        print(f"\n[{index}] {email['subject']}")
        print(f"    Från: {email['from']}")

        # 1. AI klassificerar
        mail_type, data = self.classify_email(email)
        print(f"    → Typ: {mail_type.upper()}")

        # 2. Anropa rätt handler via MCP-tool (servern utför arbete)
        if mail_type == "support":
            await self.call_tool("handle_support_email", {
                "from_email": email['from'],
                "subject": email['subject'],
                "body": email['body']
            })

        elif mail_type == "sales":
            product = data.get("product", "produkt")
            await self.call_tool("handle_sales_email", {
                "from_email": email['from'],
                "subject": email['subject'],
                "product_query": product if product else "produkt"
            })

        elif mail_type == "estimate":
            description = data.get("project_description", email['body'])
            await self.call_tool("handle_estimate_email", {
                "from_email": email['from'],
                "subject": email['subject'],
                "project_description": description
            })

        elif mail_type == "meeting":
            meeting_time = data.get("meeting_time")
            args = {
                "from_email": email['from'],
                "subject": email['subject']
            }
            if meeting_time:
                args["meeting_time"] = meeting_time
            await self.call_tool("handle_meeting_email", args)

    async def run(self):
        """Kör agenten."""
        print("\n" + "======================================================")
        print("  MCP MAIL-AGENT")
        print("======================================================")

        # Hämta mail via MCP-tool
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

        print("\n" + "======================================================")
        print(f"  KLART! Hanterade {len(emails)} mail")
        print("======================================================")


async def run_once():
    """Kör agenten en gång."""
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
            agent = MailAgent(session)
            await agent.run()


async def main():
    """Startar agenten med eller utan loop."""
    parser = argparse.ArgumentParser(description="MCP Mail Agent")
    parser.add_argument("--loop", nargs="?", const=5, type=int, metavar="MINUTER",
                        help="Kör kontinuerligt (standard: var 5:e minut)")
    args = parser.parse_args()

    if args.loop:
        interval_minutes = args.loop
        print(f"Startar i loop-läge (var {interval_minutes}:e minut)")
        print("Tryck Ctrl+C för att avsluta\n")

        while True:
            try:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n[{timestamp}] Kollar mail...")
                await run_once()

                print(f"\nVäntar {interval_minutes} minuter till nästa körning...")
                await asyncio.sleep(interval_minutes * 60)

            except KeyboardInterrupt:
                print("\n\nAvslutar...")
                break
    else:
        await run_once()


if __name__ == "__main__":
    asyncio.run(main())
