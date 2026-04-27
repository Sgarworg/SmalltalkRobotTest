from typing import Any
import httpx
import sys
from claude_agent_sdk import tool, create_sdk_mcp_server
from database import recipes
from tinydb import Query



recipes.insert({
    "name": "test name",
    "zutaten": "test zutate",
    "anleitung": "test aleitung",
    "kochzeit": "test kochzeit",
    "kategorie": "test kategorie",
})