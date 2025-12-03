"""Core-moduler för Bengtssons Trävaror MCP-server."""

from .products import PRODUCTS
from .agents import SalesAgent, ComplaintAgent

__all__ = [
    "PRODUCTS",
    "SalesAgent",
    "ComplaintAgent",
]
