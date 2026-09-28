import os
import json
import urllib.request
import urllib.parse

def search_online_recipes(query: str) -> str:
    """Fetch live recipe ideas and inspiration from TheMealDB public recipe API.

    Args:
        query: Search term for online recipe search (e.g. 'pasta', 'chicken', 'curry').

    Returns:
        A formatted string summarizing online recipe search results with dish names, origin, and instructions snippet.
    """
    api_key = os.getenv("THEMEALDB_API_KEY", "1")
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.themealdb.com/api/json/v1/{api_key}/search.php?s={encoded_query}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "RecipeConcierge/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        meals = data.get("meals")
        if not meals:
            return f"No online recipes found matching '{query}'."

        results = []
        for meal in meals[:3]:
            name = meal.get("strMeal")
            category = meal.get("strCategory", "Main")
            area = meal.get("strArea", "")
            instructions = meal.get("strInstructions", "").replace("\r\n", " ")
            snippet = instructions[:180] + "..." if len(instructions) > 180 else instructions
            thumb = meal.get("strMealThumb")

            results.append(
                f"• {name} ({area} {category})\n"
                f"  Summary: {snippet}\n"
                f"  Image: {thumb}"
            )

        return f"Found {len(results)} recipe(s) online for '{query}':\n\n" + "\n\n".join(results)
    except Exception as e:
        return f"Error fetching online recipes: {str(e)}"
