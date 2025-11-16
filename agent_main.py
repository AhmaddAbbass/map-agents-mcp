import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from agents import Agent, Runner
from agents.mcp import MCPServerStdio

# --- load env (for OPENAI_API_KEY etc.) ---
ROOT = Path(__file__).parent
load_dotenv(dotenv_path=ROOT / ".env", override=True)

PYTHON_EXE = sys.executable  # ensures we use the venv python


async def main() -> None:
    """
    Run an interactive map assistant backed by our two MCP servers:

    - OSM Geocoding server:
        * search_place
        * reverse_geocode
        * search_pois

    - OSRM Routing server:
        * route_between
        * route_summary
        * distance_matrix
    """

    # Start both MCP servers as subprocesses over stdio
    async with MCPServerStdio(
        name="OSM Geocoding Server",
        params={
            "command": PYTHON_EXE,
            "args": ["-m", "servers.osm_geocode_server"],
        },
    ) as osm_server, MCPServerStdio(
        name="OSRM Routing Server",
        params={
            "command": PYTHON_EXE,
            "args": ["-m", "servers.osrm_routing_server"],
        },
    ) as osrm_server:

        # NOTE: If you don't set model=..., Agents SDK defaults to gpt-4.1-mini
        # (as long as OPENAI_API_KEY is set). 
        map_agent = Agent(
            name="Beirut Map Assistant",
            instructions=(
                "You are a helpful map assistant focused on Beirut and nearby areas.\n"
                "- Use the OSM tools for geocoding, reverse geocoding, and POI search.\n"
                "- Use the OSRM tools for routing, route summaries, and distance matrices.\n"
                "- Always explain briefly what you are doing, then summarize results clearly.\n"
            ),
            mcp_servers=[osm_server, osrm_server],
        )

        print("✅ Map agent is ready.")
        print("Type a question about places/routes (or 'quit' to exit).\n")

        while True:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in {"q", "quit", "exit"}:
                print("Bye!")
                break

            # Run the agent with our input
            result = await Runner.run(
                starting_agent=map_agent,
                input=user_input,
            )

            print("\nAgent:\n")
            print(result.final_output)
            print("\n" + "-" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
