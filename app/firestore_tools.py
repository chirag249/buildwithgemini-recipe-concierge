import uuid
from typing import Optional, List
from google.cloud import firestore

# Hardcoded Project ID string as strictly required
FIRESTORE_PROJECT = "qwiklabs-gcp-01-0f8258c0f681"

def _get_db() -> firestore.Client:
    return firestore.Client(project=FIRESTORE_PROJECT)

def search_recipes(query: str = "", cuisine: Optional[str] = None) -> str:
    """Search recipes in the Firestore database by keyword or cuisine.

    Args:
        query: Search term to match in recipe titles, ingredients, or dietary tags. Use empty string or '*' for all.
        cuisine: Optional filter for a specific cuisine (e.g., 'Italian', 'Mexican', 'Thai').

    Returns:
        A list of matching recipe summaries.
    """
    db = _get_db()
    docs = db.collection("recipes").stream()
    
    results = []
    query_lower = query.strip().lower() if query else ""
    if query_lower in ["*", "all", "any", "everything"]:
        query_lower = ""
        
    cuisine_lower = cuisine.strip().lower() if cuisine else ""

    for doc in docs:
        data = doc.to_dict()
        title = data.get("title", "")
        c_type = data.get("cuisine", "")
        ingredients = " ".join(data.get("ingredients", []))
        tags = " ".join(data.get("dietary_tags", []))

        # Check cuisine filter if provided
        if cuisine_lower and cuisine_lower not in c_type.lower():
            continue

        # Check query term
        if (
            not query_lower
            or query_lower in title.lower()
            or query_lower in c_type.lower()
            or query_lower in ingredients.lower()
            or query_lower in tags.lower()
        ):
            results.append(
                f"- ID: {doc.id} | {title} ({c_type}, Prep: {data.get('prep_time_mins')}m)\n"
                f"  Tags: {', '.join(data.get('dietary_tags', []))}\n"
                f"  Ingredients: {', '.join(data.get('ingredients', []))}"
            )

    if not results:
        return f"No recipes found matching query '{query}'" + (f" and cuisine '{cuisine}'" if cuisine else "") + "."
    
    return f"Found {len(results)} recipe(s):\n" + "\n\n".join(results)


def get_recipe_details(recipe_id: str) -> str:
    """Retrieve full details and instructions for a specific recipe by ID.

    Args:
        recipe_id: Document ID of the recipe (e.g., 'recipe_1', 'recipe_2').

    Returns:
        A detailed view of the recipe including full instructions and ingredient list.
    """
    db = _get_db()
    doc_ref = db.collection("recipes").document(recipe_id)
    doc = doc_ref.get()

    if not doc.exists:
        return f"Recipe with ID '{recipe_id}' was not found in the database."

    data = doc.to_dict()
    title = data.get("title")
    cuisine = data.get("cuisine")
    prep_time = data.get("prep_time_mins")
    ingredients = data.get("ingredients", [])
    instructions = data.get("instructions")
    tags = data.get("dietary_tags", [])

    formatted_ingredients = "\n".join([f"  • {item}" for item in ingredients])

    return (
        f"📖 Recipe: {title}\n"
        f"Cuisine: {cuisine} | Prep Time: {prep_time} mins\n"
        f"Dietary Tags: {', '.join(tags)}\n\n"
        f"Ingredients:\n{formatted_ingredients}\n\n"
        f"Instructions:\n{instructions}"
    )


def add_recipe(
    title: str,
    cuisine: str,
    prep_time_mins: int,
    ingredients: List[str],
    instructions: str,
    dietary_tags: Optional[List[str]] = None
) -> str:
    """Add a new recipe to the Firestore database.

    Args:
        title: Title of the recipe.
        cuisine: Cuisine type (e.g., Italian, Asian, Mexican).
        prep_time_mins: Preparation time in minutes.
        ingredients: List of ingredient strings.
        instructions: Step-by-step cooking instructions.
        dietary_tags: Optional list of dietary tags (e.g. ['vegan', 'gluten-free']).

    Returns:
        Confirmation message with the created recipe ID.
    """
    db = _get_db()
    doc_id = f"recipe_{uuid.uuid4().hex[:8]}"
    
    recipe_data = {
        "id": doc_id,
        "title": title,
        "cuisine": cuisine,
        "prep_time_mins": prep_time_mins,
        "ingredients": ingredients,
        "instructions": instructions,
        "dietary_tags": dietary_tags or []
    }

    db.collection("recipes").document(doc_id).set(recipe_data)
    return f"Successfully saved new recipe '{title}' with ID '{doc_id}' to Firestore."


def generate_grocery_shopping_list(recipe_ids: List[str]) -> str:
    """Generate a consolidated grocery shopping list from one or more recipe IDs.

    Args:
        recipe_ids: A list of recipe document IDs (e.g. ['recipe_1', 'recipe_2']).

    Returns:
        A formatted, consolidated shopping list grouped by recipe.
    """
    db = _get_db()
    shopping_items = []
    recipe_titles = []

    for rid in recipe_ids:
        doc = db.collection("recipes").document(rid).get()
        if doc.exists:
            data = doc.to_dict()
            title = data.get("title", rid)
            recipe_titles.append(title)
            ingredients = data.get("ingredients", [])
            for ing in ingredients:
                shopping_items.append(f"• {ing} (for {title})")
        else:
            shopping_items.append(f"• [Recipe ID '{rid}' not found]")

    if not shopping_items:
        return "No valid recipes were provided to generate a shopping list."

    titles_str = ", ".join(recipe_titles)
    list_str = "\n".join(shopping_items)
    return f"🛒 Grocery Shopping List for [{titles_str}]:\n\n{list_str}"

