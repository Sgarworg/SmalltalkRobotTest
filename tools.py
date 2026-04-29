from typing import Any
import httpx
import sys
from database import recipes
from tinydb import Query


async def get_temperature(args: dict[str, Any]) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": args["latitude"],
                "longitude": args["longitude"],
                "current": "temperature_2m",
                "temperature_unit": "fahrenheit",
            },
        )
        data = response.json()
    return f"Temperature: {data['current']['temperature_2m']}°F"


async def get_rain(args: dict[str, Any]) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": args["latitude"],
                "longitude": args["longitude"],
                "current": "precipitation,rain",
                "hourly": "precipitation_probability",
                "forecast_days": 1,
            },
        )
        data = response.json()
    current = data["current"]
    rain_prob = data["hourly"]["precipitation_probability"][0]
    return f"Niederschlag: {current['precipitation']}mm, Regen: {current['rain']}mm, Regenwahrscheinlichkeit: {rain_prob}%"


async def get_joke(args: dict[str, Any]) -> str:
    category = args.get("category", "Any")
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://v2.jokeapi.dev/joke/{category}",
            params={"lang": "de", "type": "twopart"},
        )
        data = response.json()
    return f"{data['setup']} - {data['delivery']}\n\nAnweisung: Erkläre ihn nicht und frag danach ob der Nutzer noch einen möchte."


async def exit_app(args: dict[str, Any]) -> str:
    sys.exit(0)


async def save_recipe(args: dict[str, Any]) -> str:
    recipes.insert({
        "name": args["name"],
        "zutaten": args["zutaten"],
        "anleitung": args["anleitung"],
        "kochzeit": args.get("kochzeit", 0),
        "kategorie": args.get("kategorie", ""),
    })
    return f"Rezept '{args['name']}' gespeichert!"


async def get_recipes(args: dict[str, Any]) -> str:
    name = args.get("name", "")
    if name:
        R = Query()
        result = recipes.search(R.name.matches(name, flags=2))
    else:
        result = recipes.all()
    return str(result)


async def delete_recipe(args: dict[str, Any]) -> str:
    R = Query()
    recipes.remove(R.name == args["name"])
    return f"Rezept '{args['name']}' gelöscht!"


TOOL_MAP = {
    "get_temperature": get_temperature,
    "get_rain": get_rain,
    "get_joke": get_joke,
    "exit_app": exit_app,
    "save_recipe": save_recipe,
    "get_recipes": get_recipes,
    "delete_recipe": delete_recipe,
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_temperature",
            "description": "Get the current temperature at a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "latitude": {"type": "number"},
                    "longitude": {"type": "number"},
                },
                "required": ["latitude", "longitude"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_rain",
            "description": "Get the current precipitation and rain probability at a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "latitude": {"type": "number"},
                    "longitude": {"type": "number"},
                },
                "required": ["latitude", "longitude"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_joke",
            "description": "Get a random joke in a specific category. Categories: Programming, Misc, Dark, Pun, Spooky, Christmas, Any",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                },
                "required": ["category"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "exit_app",
            "description": "WICHTIG: Dieses Tool MUSS aufgerufen werden wenn der Nutzer die Anwendung beenden will. Beispiele: 'geh weg', 'tschüss', 'exit', 'auf wiedersehen', 'ich bin fertig', fluchen.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_recipe",
            "description": "Speichert ein Rezept in der Datenbank.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "zutaten": {"type": "string"},
                    "anleitung": {"type": "string"},
                    "kochzeit": {"type": "integer"},
                    "kategorie": {"type": "string"},
                },
                "required": ["name", "zutaten", "anleitung"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_recipes",
            "description": "Gibt alle Rezepte oder ein bestimmtes Rezept aus der Datenbank zurück.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_recipe",
            "description": "Löscht ein Rezept aus der Datenbank anhand des Namens.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                },
                "required": ["name"],
            },
        },
    },
]