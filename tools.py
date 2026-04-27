from typing import Any
import httpx
import sys
from claude_agent_sdk import tool, create_sdk_mcp_server
from database import recipes
from tinydb import Query



@tool(
    "get_temperature",
    "Get the current temperature at a location",
    {"latitude": float, "longitude": float},
)
async def get_temperature(args: dict[str, Any]) -> dict[str, Any]:
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

    return {
        "content": [
            {
                "type": "text",
                "text": f"Temperature: {data['current']['temperature_2m']}°F",
            }
        ]
    }


@tool(
    "get_rain",
    "Get the current precipitation and rain probability at a location",
    {"latitude": float, "longitude": float},
)
async def get_rain(args: dict[str, Any]) -> dict[str, Any]:
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

    return {
        "content": [
            {
                "type": "text",
                "text": f"Niederschlag: {current['precipitation']}mm, Regen: {current['rain']}mm, Regenwahrscheinlichkeit: {rain_prob}%",
            }
        ]
    }


@tool(
    "get_joke",
    "Get a random joke in a specific category. Categories: Programming, Misc, Dark, Pun, Spooky, Christmas, Any",
    {"category": str},
)
async def get_joke(args: dict[str, Any]) -> dict[str, Any]:
    category = args.get("category", "Any")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://v2.jokeapi.dev/joke/{category}",
            params={"lang": "de", "type": "twopart"},
        )
        data = response.json()

    return {
        "content": [
            {
                "type": "text",
                "text": f"{data['setup']} - {data['delivery']}\n\nAnweisung: Erkläre ihn nicht und frag danach ob der Nutzer noch einen möchte.",
            }
        ]
    }


@tool(
    "exit_app",
    "WICHTIG: Dieses Tool MUSS aufgerufen werden wenn der Nutzer die Anwendung beenden will. Beispiele: 'geh weg', 'tschüss', 'exit', 'auf wiedersehen', 'ich bin fertig', fluchen. Rufe dieses Tool SOFORT auf ohne zu antworten.",
    {},
)
async def exit_app(args: dict[str, Any]) -> dict[str, Any]:
    sys.exit(0)

@tool(
    "save_recipe",
    "Speichert ein Rezept in der Datenbank.",
    {"name": str, "zutaten": str, "anleitung": str, "kochzeit": int, "kategorie": str},
)
async def save_recipe(args: dict[str, Any]) -> dict[str, Any]:
    print(f" save_recipe aufgerufen mit: {args}")
    recipes.insert({
        "name": args["name"],
        "zutaten": args["zutaten"],
        "anleitung": args["anleitung"],
        "kochzeit": args.get("kochzeit", 0),
        "kategorie": args.get("kategorie", ""),
    })
    print("Rezept gespeichert!")
    return {"content": [{"type": "text", "text": f"Rezept '{args['name']}' gespeichert!"}]}


@tool(
    "get_recipes",
    "Gibt alle Rezepte oder ein bestimmtes Rezept aus der Datenbank zurück.",
    {"name": str},
)
async def get_recipes(args: dict[str, Any]) -> dict[str, Any]:
    print(f" get_recipe aufgerufen mit: {args}")
    name = args.get("name", "")
    if name:
        R = Query()
        result = recipes.search(R.name.matches(name, flags=2))  # case insensitive
    else:
        result = recipes.all()
    print(result)
    return {"content": [{"type": "text", "text": str(result)}]}


@tool(
    "delete_recipe",
    "Löscht ein Rezept aus der Datenbank anhand des Namens.",
    {"name": str},
)
async def delete_recipe(args: dict[str, Any]) -> dict[str, Any]:
    R = Query()
    recipes.remove(R.name == args["name"])
    return {"content": [{"type": "text", "text": f"Rezept '{args['name']}' gelöscht!"}]}

tools_server = create_sdk_mcp_server(
    name="tools",
    version="1.0.0",
    tools=[get_temperature, get_rain, get_joke, exit_app,save_recipe,get_recipes,delete_recipe ],
)