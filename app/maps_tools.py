import os
import json
import urllib.request
import urllib.parse
from typing import Optional

def _get_maps_api_key() -> str:
    key = os.getenv("GOOGLE_MAPS_API_KEY", "").strip()
    return key

def geocode_address(address: str) -> str:
    """Turn a street address or city name into geographic coordinates (latitude and longitude).

    Args:
        address: Street address, landmark, or city name to geocode (e.g. '1600 Amphitheatre Pkwy, Mountain View, CA' or 'San Francisco').

    Returns:
        A formatted string with the geocoded address, latitude, and longitude.
    """
    api_key = _get_maps_api_key()
    if not api_key or api_key == "PASTE_KEY_HERE":
        return "Error: GOOGLE_MAPS_API_KEY is not set or contains default placeholder in .env."

    encoded_address = urllib.parse.quote(address)
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        status = data.get("status")
        if status != "OK" or not data.get("results"):
            return f"Geocoding failed for '{address}'. Status: {status}"

        result = data["results"][0]
        formatted_address = result.get("formatted_address", address)
        location = result["geometry"]["location"]
        lat = location["lat"]
        lng = location["lng"]

        return (
            f"📍 Geocode Result:\n"
            f"  • Address: {formatted_address}\n"
            f"  • Location: ({lat}, {lng})"
        )
    except Exception as e:
        return f"Error executing Geocoding request: {str(e)}"


def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "supermarket",
    radius_meters: float = 2000.0
) -> str:
    """Find nearby places of a given type around latitude/longitude coordinates using Places API (New).

    Args:
        latitude: Latitude coordinate of center point.
        longitude: Longitude coordinate of center point.
        place_type: Place type to filter (e.g. 'supermarket', 'grocery_store', 'restaurant', 'bakery').
        radius_meters: Search radius in meters (default: 2000m).

    Returns:
        A list of nearby places with name, address, and location coordinates.
    """
    api_key = _get_maps_api_key()
    if not api_key or api_key == "PASTE_KEY_HERE":
        return "Error: GOOGLE_MAPS_API_KEY is not set or contains default placeholder in .env."

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location"
    }

    body = {
        "includedTypes": [place_type],
        "maxResultCount": 10,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "radius": float(radius_meters)
            }
        }
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        places = data.get("places", [])
        if not places:
            return f"No nearby places of type '{place_type}' found within {radius_meters}m of ({latitude}, {longitude})."

        results = []
        for p in places:
            name = p.get("displayName", {}).get("text", "Unknown Name")
            address = p.get("formattedAddress", "N/A")
            loc = p.get("location", {})
            p_lat = loc.get("latitude")
            p_lng = loc.get("longitude")

            results.append(
                f"• **{name}**\n"
                f"  Address: {address}\n"
                f"  Location: ({p_lat}, {p_lng})"
            )

        return f"Found {len(results)} nearby '{place_type}' place(s):\n\n" + "\n\n".join(results)
    except Exception as e:
        return f"Error executing Places API (New) search: {str(e)}"
