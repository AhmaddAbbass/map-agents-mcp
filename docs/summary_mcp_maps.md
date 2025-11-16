# MCP + Map Servers Summary

## Key MCP Concepts (from Hugging Face article)

The Hugging Face article presents the **Model Context Protocol (MCP)** as an open, vendor-neutral standard that lets AI agents talk to external tools and data sources through a unified interface. Instead of wiring custom integrations for each API, developers run **MCP servers** that expose tools (functions) and resources over a structured protocol. Any compatible MCP client (Claude Desktop, OpenAI Agents SDK, LangChain adapter, etc.) can auto-discover those tools and call them at runtime. :contentReference[oaicite:3]{index=3}

The article explains how MCP sits inside an agentic workflow: it is not the “brain” of the agent, but the **Action layer**. The agent keeps its usual capabilities (reasoning, planning, memory), while MCP standardises how it triggers actions such as reading files, querying a database, or calling a SaaS API. This reduces integration from an “N×M” mess of bespoke connectors to an “N+M” model, where any client can reuse any server. :contentReference[oaicite:4]{index=4}

MCP also emphasises **two-way, stateful interactions** rather than just one-shot calls. Servers can expose multiple tools plus richer metadata and prompts, and clients can maintain sessions. The ecosystem is growing quickly, with community servers for Google Drive, Git, databases, web browsers and more, and future work around remote servers, OAuth, registries and well-known endpoints is already in progress. :contentReference[oaicite:5]{index=5}

## Map Server Features and Design Patterns

Existing map servers such as **Nominatim** (OpenStreetMap), **OSRM**, and other routing / geocoding APIs share several recurring patterns:

1. **Clear separation of concerns**  
   - Nominatim focuses on **geocoding** and **reverse geocoding**: converting addresses or place names to coordinates and back, using `/search` and `/reverse` endpoints. :contentReference[oaicite:6]{index=6}  
   - OSRM focuses on **routing and distance matrices**, offering endpoints like `/route`, `/table`, `/trip` and `/nearest` over HTTP JSON APIs. :contentReference[oaicite:7]{index=7}  

2. **Simple, parameter-based HTTP interfaces**  
   Both families use query parameters such as `q`, `lat`, `lon`, or lists of coordinates. They return compact JSON with coordinates, display names, step-by-step routes, durations and distances, designed to be machine-readable and easy to compose into higher-level tools.

3. **Stateless requests with rate-limit and usage policies**  
   The servers are stateless and horizontally scalable, but enforce politeness: Nominatim requires custom User-Agent strings and discourages bulk geocoding from the public instance. :contentReference[oaicite:8]{index=8}

4. **Composable building blocks**  
   Most map workflows chain together smaller operations: “geocode origin → geocode destination → compute route → possibly query nearby POIs”. This maps nicely onto MCP’s idea of small, well-documented tools that agents can combine dynamically.

Our custom MCP map servers follow these patterns: small HTTP wrappers over public map APIs, exposed as tools that an OpenAI agent can compose into geocoding, routing, and POI-search workflows.
