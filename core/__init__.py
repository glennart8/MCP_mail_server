"""Core-moduler för Bengtssons Trävaror affärssystem.

Dessa moduler innehåller all delad affärslogik som används av:
- server.py (MCP-server för Claude Desktop)
- agent_runner.py (Demo/test-agent)
"""

from .mail import EmailClient, INBOX
from .products import PRODUCTS
from .complaints import ComplaintsSystem
from .sales import SalesSystem
from .agents import SupervisorAgent, SalesAgent, ComplaintAgent

__all__ = [
    "EmailClient",
    "INBOX",
    "PRODUCTS",
    "ComplaintsSystem",
    "SalesSystem",
    "SupervisorAgent",
    "SalesAgent",
    "ComplaintAgent",
]
