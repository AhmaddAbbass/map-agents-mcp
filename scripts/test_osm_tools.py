# scripts/test_osm_tools.py
"""
Quick smoke tests for OSM Geocoding Server tools.
This bypasses MCP and calls the functions directly.

We modify sys.path so this script can find the `servers` package
when run as `python scripts/test_osm_tools.py` from the project root.
"""

import os
import sys

# Add project root to sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from servers.osm_geocode_server import (
    search_place,
    reverse_geocode,
    search_pois,
)


def main():
    print("=== OSM Geocoding: search_place ===")
    res = search_place("American University of Beirut", limit=1)
    print(res)

    if res:
        lat = res[0]["lat"]
        lon = res[0]["lon"]

        print("\n=== OSM Geocoding: reverse_geocode ===")
        rev = reverse_geocode(lat, lon)
        print(rev)

        print("\n=== OSM Geocoding: search_pois (cafes near AUB) ===")
        pois = search_pois("cafe", lat, lon, radius_m=800, limit=3)
        print(pois)
    else:
        print("No result from search_place; cannot run further tests.")


if __name__ == "__main__":
    main()
