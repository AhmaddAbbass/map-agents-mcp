# scripts/test_osrm_tools.py
"""
Quick smoke tests for OSRM Routing Server tools.

We modify sys.path so this script can find the `servers` package
when run as `python scripts/test_osrm_tools.py` from the project root.
"""

import os
import sys

# Add project root to sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from servers.osrm_routing_server import route_between, route_summary, distance_matrix


def main():
    # Rough coordinates for AUB and Beirut–Rafic Hariri International Airport
    aub = {"lat": 33.9011, "lon": 35.4804}
    airport = {"lat": 33.8209, "lon": 35.4884}

    print("=== OSRM: route_between (AUB -> Airport) ===")
    route = route_between(
        start_lat=aub["lat"],
        start_lon=aub["lon"],
        end_lat=airport["lat"],
        end_lon=airport["lon"],
    )
    print(route)

    print("\n=== OSRM: route_summary ===")
    print(
        route_summary(
            start_lat=aub["lat"],
            start_lon=aub["lon"],
            end_lat=airport["lat"],
            end_lon=airport["lon"],
        )
    )

    print("\n=== OSRM: distance_matrix (AUB, Airport, random point) ===")
    random_point = {"lat": 33.90, "lon": 35.50}
    matrix = distance_matrix([aub, airport, random_point])
    print(matrix)


if __name__ == "__main__":
    main()
