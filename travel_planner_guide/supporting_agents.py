from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from travel_planner_guide.tools import google_search_grounding

LLM="gemini-2.5-flash"

# Supporting agents for news

travel_news_agent = Agent(
    model = LLM,
    name= "travel_news_agent",
    description= "Suggest key travel events and news; uses search for current information.", 

    instruction = """
           You are reponsible for providing list of event and news based on user's inspiration  query.
           Limit the choices to 10 results. You need to use the google_search_grounding tool to search current information.
            """,
    tools = [google_search_grounding]
    
)

#location finding agent
from travel_planner_guide.tools import location_search_tool

places_agent = Agent(
    model = LLM,
    name= "places_agent",
    description= "Suggest places near famous locations based on user preferendes", 

    instruction = """
           You are responsible for making suggestions on actual places based on the user's query. Limit the results to 10 results.
           Each place must have a name, location, and address.
           You can use the `location_search_tool` to find nearby places based on a query and a location. This tool returns a list of matching place names and addresses.
""",
    tools = [location_search_tool]
    
)




# Inspiration supporting agents here
travel_inspiration_agent = Agent(
    model = LLM,
    name= "travel_inspiration_agent",
    description= "Inspires users with travel ideas.",
    instruction = """
            You are travel inspiration agent who helps users find their  next big dream vacation destinations.
            Your role and goal is to help the user  identify a destination and a few activities at the destination .
            As part of that, user may ask you for general history or knowledge about a dstination, in that scenario, answer briefly in the best of your ability, but focus on the goal by relationg your answer back to destination and activities the user may in . 
            
            - You will call the two tool ' place_agent(inspiration query)' and 'news_agent(inspiration query)' when appropriate:
            - Use 'news_agent' to provide key events and news recommendations based on the user's query .
            - Use 'place_agent' to provide a list of locations or nearby places to famous locations when user asks for it,  for example, "find hotels near eiffel tower" should return nearby hotels given some user preferences.
            """,
    tools = [AgentTool(agent=travel_news_agent), AgentTool(agent=places_agent)]
)
