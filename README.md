# MCP Map Agents – OSM + OSRM

This repo implements **2 custom MCP map servers** and an **OpenAI Agent** that uses them:

1. `OSM Geocoding Server` – wraps OpenStreetMap Nominatim for:
   - Forward geocoding (`search_place`)
   - Reverse geocoding (`reverse_geocode`)
   - Simple POI search (`search_pois`)

2. `OSRM Routing Server` – wraps the OSRM demo API for:
   - Driving routes (`route_between`)
   - Route text summary (`route_summary`)
   - Distance matrix (`distance_matrix`)

An `Agent` built with the **OpenAI Agents SDK** connects to both servers using `MCPServerStdio`, so it can dynamically pick the right map tools based on user queries.

---

## Setup

```bash
git clone <your-repo-url>   # or use the folder you already created
cd mcp-map-agents

python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows

pip install -r requirements.txt

cp .env.example .env
# Edit .env and set OPENAI_API_KEY and NOMINATIM_USER_AGENT
