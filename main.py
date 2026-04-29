import asyncio
from tools import tools_server
from voice_input import transcribe
from voice_output import speak
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, ResultMessage, AssistantMessage, ToolUseBlock
from config import config



async def main():
    options = ClaudeAgentOptions(
        mcp_servers={"tools": tools_server},
        allowed_tools=["mcp__tools__get_temperature", "mcp__tools__get_rain", "mcp__tools__get_joke", "mcp__tools__exit_app", "delete_recipe", "get_recipes","save_recipe"],
        system_prompt=config["system_prompt"],
        permission_mode="bypassPermissions",
    )

    async with ClaudeSDKClient(options=options) as client:
        while True:
            user_input = transcribe()
            print(f"Du: {user_input}")

            if not user_input.strip():
                print("Nichts verstanden, nochmal versuchen...")
                continue

            if user_input.lower().strip() in ["stop", "beenden", "tschüss"]:
                print("Auf Wiedersehen!")
                break

            await client.query(user_input)
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, ToolUseBlock):
                            print(f"Tool verwendet: {block.name}")
                if isinstance(message, ResultMessage):
                    print(f"Claude: {message.result}")
                    speak(message.result)


asyncio.run(main())