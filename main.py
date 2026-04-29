import asyncio
from ollama import AsyncClient
from voice.input import transcribe
from voice.output import speak
from core.config import config
from core.tools import TOOLS, TOOL_MAP


async def main():
    client = AsyncClient()
    messages = [{"role": "system", "content": config["system_prompt"]}]

    while True:
        user_input = transcribe()
        print(f"Du: {user_input}")

        if not user_input.strip():
            print("Nichts verstanden, nochmal versuchen...")
            continue

        messages.append({"role": "user", "content": user_input})

        while True:
            response = await client.chat(
                model=config["ollama_model"],
                messages=messages,
                tools=TOOLS,
            )

            msg = response.message
            messages.append({"role": msg.role, "content": msg.content or "", "tool_calls": msg.tool_calls})

            if msg.tool_calls:
                for tool_call in msg.tool_calls:
                    name = tool_call.function.name
                    args = dict(tool_call.function.arguments)
                    print(f"Tool verwendet: {name}")
                    result = await TOOL_MAP[name](args)
                    messages.append({"role": "tool", "content": result})
            else:
                print(f"Assistent: {msg.content}")
                speak(msg.content)
                break


asyncio.run(main())