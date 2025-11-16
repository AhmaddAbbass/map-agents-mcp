# servers/osrm_routing_server.py
"""
OSRM Routing MCP Server

Wraps the public OSRM demo API for:
- Driving routes between two coordinates (route_between)
- Human-readable route summary (route_summary)
- Simple distance matrix between up to ~10 waypoints (distance_matrix)

Uses the OSRM HTTP API documented here: http://project-osrm.org/docs/v5.10.0/api/ :contentReference[oaicite:12]{index=12}
"""

from typing import List, Dict, Any

import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("OSRM Routing Server")

OSRM_BASE = "http://router.project-osrm.org"


def _build_coords(coords: List[Dict[str, float]]) -> str:
    """
    Convert [{'lat': 33.9, 'lon': 35.5}, ...] to 'lon1,lat1;lon2,lat2;...'
    (OSRM expects lon,lat order.)
    """
    parts = []
    for c in coords:
        lat = c["lat"]
        lon = c["lon"]
        parts.append(f"{lon},{lat}")
    return ";".join(parts)


def _osrm_get(path: str, params: Dict[str, Any]) -> Any:
    url = f"{OSRM_BASE}{path}"
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


@mcp.tool()
def route_between(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
) -> Dict[str, Any]:
    """
    Get a driving route between two points using OSRM /route.

    Returns:
        {
          "distance_km": float,
          "duration_min": float,
          "steps": [ { "name": str, "distance_m": float, "duration_s": float, "instruction": str }, ... ]
        }
    """
    coords = _build_coords(
        [
            {"lat": start_lat, "lon": start_lon},
            {"lat": end_lat, "lon": end_lon},
        ]
    )

    data = _osrm_get(
        f"/route/v1/driving/{coords}",
        {
            "overview": "false",
            "steps": "true",
        },
    )

    if not data.get("routes"):
        return {"distance_km": None, "duration_min": None, "steps": []}

    route = data["routes"][0]
    distance_km = route["distance"] / 1000.0
    duration_min = route["duration"] / 60.0

    steps = []
    for leg in route.get("legs", []):
        for step in leg.get("steps", []):
            steps.append(
                {
                    "name": step.get("name"),
                    "distance_m": step.get("distance"),
                    "duration_s": step.get("duration"),
                    "instruction": step.get("maneuver", {}).get("instruction"),
                }
            )

    return {
        "distance_km": distance_km,
        "duration_min": duration_min,
        "steps": steps,
    }


@mcp.tool()
def route_summary(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
) -> str:
    """
    Simple human-readable summary of the route between two points.

    Useful for LLM output: it calls route_between() internally and formats a short string.
    """
    route = route_between(start_lat, start_lon, end_lat, end_lon)
    if route["distance_km"] is None:
        return "No route found."

    return (
        f"Driving distance: {route['distance_km']:.1f} km, "
        f"estimated duration: {route['duration_min']:.1f} minutes."
    )


@mcp.tool()
def distance_matrix(
    points: List[Dict[str, float]],
) -> Dict[str, Any]:
    """
    Compute a simple travel-time matrix between multiple waypoints using OSRM /table.

    Args:
        points: list of { "lat": float, "lon": float } dictionaries.

    Returns:
        {
          "durations_min": [[float, ...], ...],
          "num_points": int
        }
    """
    if not points:
        return {"durations_min": [], "num_points": 0}

    coords = _build_coords(points)

    data = _osrm_get(
        f"/table/v1/driving/{coords}",
        {"annotations": "duration"},
    )

    durations = data.get("durations")
    if durations is None:
        return {"durations_min": [], "num_points": len(points)}

    durations_min = [
        [cell / 60.0 if cell is not None else None for cell in row]
        for row in durations
    ]

    return {
        "durations_min": durations_min,
        "num_points": len(points),
    }


if __name__ == "__main__":
    mcp.run()
