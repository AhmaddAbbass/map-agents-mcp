# servers/osm_geocode_server.py
"""
OSM Geocoding MCP Server

Wraps OpenStreetMap Nominatim API for:
- Forward geocoding (search_place)
- Reverse geocoding (reverse_geocode)
- Simple POI search around a point (search_pois)

This file is a standalone MCP server when run as:
    python -m servers.osm_geocode_server

It uses FastMCP from the official Python MCP SDK. :contentReference[oaicite:9]{index=9}
"""

import os
from typing import List, Dict, Any

import requests
from mcp.server.fastmcp import FastMCP

# Create the MCP server instance
mcp = FastMCP("OSM Geocoding Server")

NOMINATIM_BASE = "https://nominatim.openstreetmap.org"


def _get_user_agent() -> str:
    # Nominatim requires a custom User-Agent and discourages bulk geocoding. :contentReference[oaicite:10]{index=10}
    ua = os.getenv("NOMINATIM_USER_AGENT")
    if not ua:
        ua = "mcp-map-assignment/0.1 (PLEASE_SET_NOMINATIM_USER_AGENT)"
    return ua


def _request(path: str, params: Dict[str, Any]) -> Any:
    headers = {"User-Agent": _get_user_agent()}
    url = f"{NOMINATIM_BASE}{path}"
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()


@mcp.tool()
def search_place(query: str, limit: int = 3) -> List[Dict[str, Any]]:
    """
    Forward geocoding using Nominatim /search.

    Args:
        query: Free-form text (e.g. "Beirut, Lebanon" or "American University of Beirut")
        limit: Maximum number of results to return.

    Returns:
        A list of objects with:
            - display_name: human-readable name
            - lat: latitude as float
            - lon: longitude as float
    """
    data = _request(
        "/search",
        {
            "q": query,
            "format": "jsonv2",  # JSON v2 is simpler to parse :contentReference[oaicite:11]{index=11}
            "limit": limit,
        },
    )

    results = []
    for item in data:
        try:
            lat = float(item.get("lat"))
            lon = float(item.get("lon"))
        except (TypeError, ValueError):
            continue

        results.append(
            {
                "display_name": item.get("display_name"),
                "lat": lat,
                "lon": lon,
            }
        )

    return results


@mcp.tool()
def reverse_geocode(lat: float, lon: float) -> Dict[str, Any]:
    """
    Reverse geocoding using Nominatim /reverse.

    Args:
        lat: Latitude in WGS84
        lon: Longitude in WGS84

    Returns:
        A dict containing:
            - display_name: full address string
            - lat, lon: location of the resolved place
            - address: structured address components if available
    """
    data = _request(
        "/reverse",
        {
            "lat": lat,
            "lon": lon,
            "format": "jsonv2",
            "addressdetails": 1,
        },
    )

    return {
        "display_name": data.get("display_name"),
        "lat": float(data.get("lat", lat)),
        "lon": float(data.get("lon", lon)),
        "address": data.get("address", {}),
    }


@mcp.tool()
def search_pois(
    query: str,
    lat: float,
    lon: float,
    radius_m: int = 1000,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """
    Very simple POI "search" by combining a text query with a viewbox around a point.

    Args:
        query: e.g. "cafe", "museum", "hospital"
        lat, lon: center point
        radius_m: approximate radius in meters for the search box
        limit: max results

    NOTE:
        This is intentionally simple and not a full Overpass wrapper. It just uses
        Nominatim's viewbox filtering, which is good enough for this assignment.
    """
    # Very crude bounding-box approximation (lat/lon degrees)
    # 1 degree lat ~ 111 km; we scale radius accordingly.
    delta_deg = radius_m / 111_000.0
    north = lat + delta_deg
    south = lat - delta_deg
    east = lon + delta_deg
    west = lon - delta_deg

    data = _request(
        "/search",
        {
            "q": query,
            "format": "jsonv2",
            "limit": limit,
            "viewbox": f"{west},{north},{east},{south}",
            "bounded": 1,
        },
    )

    results = []
    for item in data:
        try:
            item_lat = float(item.get("lat"))
            item_lon = float(item.get("lon"))
        except (TypeError, ValueError):
            continue

        results.append(
            {
                "name": item.get("display_name"),
                "lat": item_lat,
                "lon": item_lon,
                "category": item.get("category"),
                "type": item.get("type"),
            }
        )

    return results


if __name__ == "__main__":
    # When run directly, start the MCP server.
    # For Agents SDK we will connect via stdio (MCPServerStdio).
    mcp.run()
