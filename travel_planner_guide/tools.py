from google.adk.tools.google_search_tool import google_search
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

LLM="gemini-2.5-flash"


_search_agent = Agent(
    model = LLM,
    name= "google_search_wrapped_agent",
    description= "An agent providing Google-search grounding capability.",
    instruction = """
        Answer the user's query by using the google search grounding tool; provide a brief but concise information.
        Rather then a detailed response,  provide the immediate actionable item for a tourist or traveler, in a concise manner.
        Do not ask the user to check or look up information tor themselves, that's your role; do your best to provide the information directly.
        IMPORTANT:
        - Always return your response in bullet points
        - Specify what matters to the user
    """,
    tools = [google_search],   
)

google_search_grounding = AgentTool(_search_agent)

#we will define a function agent to suggest places near famous location where travelers stay.
from google.adk.tools import FunctionTool

#we install geopy to get lat and long from address(uv add geopy)and use openstreetmap api to get nearby places.
from geopy.geocoders import Nominatim
import requests
import json # Import json for better error handling

from requests.exceptions import RequestException, ConnectionError, Timeout, HTTPError

def find_nearby_places_open(query: str, location:str, radius: int = 3000, limit: int = 5) ->str:
    """
    Find nearby places for any text query using ONLY free OpenStreetMap APIs(no API key needed).

    Args:
        query (str): What you're looking for(e.g., "restautant", "hospital", "gym").
        location (str): The city or area to serarch in.
        radius (int): Search radius in meters (default: 3000m).
        limit (int):  Number of results to show (default:5).

    Returns:
        str: List of matching place names and addresses.
    """
    try:
        # Input Validation (Optional but Recommended)
        if not query.strip():
            return "Error: Query cannot be empty."
        if not location.strip():
            return "Error: Location cannot be empty."
        if not isinstance(radius, int) or radius <= 0:
            return "Error: Radius must be a positive integer."
        if not isinstance(limit, int) or limit <= 0:
            return "Error: Limit must be a positive integer."

        # Step 1: Geocode the location to get coordinates
        geolocator = Nominatim(user_agent = "open_place_finder")
        loc = geolocator.geocode(location)
        if not loc:
            return f"Could not find location '{location}'."
        latitude, longitude = loc.latitude, loc.longitude

        # Step 2: Query Overpass API to find nearby places
        overpass_url = "http://overpass-api.de/api/interpreter"
        overpass_query = f"""
        [out:json][timeout:25];
        (
            node["name"~"{query}",i](around:{radius},{latitude},{longitude});
            node["amenity"~"{query}",i](around:{radius},{latitude},{longitude});
            node["shop"~"{query}",i](around:{radius},{latitude},{longitude});
        );
        out body;
        """

        # Correctly make the GET request and assign the response
        response = requests.get(overpass_url, params={"data": overpass_query})

        # Step 3: Handle the response
        if response.status_code == 429:
            return "Overpass API Error: Rate limit exceeded. Please try again later."
        elif response.status_code != 200:
            return f"Overpass API error: Status {response.status_code}. Response text: {response.text}"

        try:
            data = response.json()
        except json.JSONDecodeError:
            return f"Error decoding JSON. Response text: {response.text}"

        elements = data.get("elements", [])
        if not elements:
            return f"No nearby places found for '{query}' in '{location}'."

        # Step 4: Format the results and apply the limit in Python
        output  = [f"Top results for '{query}' near '{location}':"]
        for el in elements[:limit]:
            name = el.get("tags", {}).get("name", "Unnamed Place")
            street = el.get("tags", {}).get("addr:street", "")
            city = el.get("tags", {}).get("addr:city", "")
            full_addr= ", ".join(filter(None, [street, city]))
            output.append(f"* {name} | {full_addr if full_addr else 'Address not available'}")
        return "\n".join(output)

    except ConnectionError:
        return f"A network connection error occurred while searching for '{query}' near '{location}'. Please check your internet connection."
    except Timeout:
        return f"The request to the API timed out while searching for '{query}' near '{location}'. The server took too long to respond."
    except RequestException as e:
        # Catch any other specific requests exceptions not caught above
        return f"An unexpected API request error occurred while searching for '{query}' near '{location}': {str(e)}"
    except Exception as e:
        # Generic error handling as a fallback for other errors
        return f"An unexpected error occurred while searching for '{query}' near '{location}': {str(e)}"


location_search_tool = FunctionTool(func = find_nearby_places_open)






