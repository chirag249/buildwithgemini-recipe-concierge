import sys
from google.cloud import firestore

FIRESTORE_PROJECT = "qwiklabs-gcp-01-0f8258c0f681"

def seed_database():
    print(f"Connecting to Firestore for project: {FIRESTORE_PROJECT}...")
    db = firestore.Client(project=FIRESTORE_PROJECT)
    collection_ref = db.collection("recipes")

    recipes = [
        {
            "id": "recipe_1",
            "title": "Creamy Tuscan Garlic Chicken",
            "cuisine": "Italian",
            "prep_time_mins": 25,
            "ingredients": [
                "2 boneless chicken breasts",
                "1 cup heavy cream",
                "1/2 cup sun-dried tomatoes",
                "2 cups spinach",
                "3 cloves garlic minced",
                "1/2 cup parmesan cheese"
            ],
            "instructions": "Sear chicken breasts in olive oil until golden. Remove chicken, sauté garlic and sun-dried tomatoes. Add heavy cream and bring to simmer. Stir in spinach and parmesan until wilted and creamy. Return chicken to pan and coat.",
            "dietary_tags": ["gluten-free", "high-protein", "keto"]
        },
        {
            "id": "recipe_2",
            "title": "Avocado & Black Bean Tacos",
            "cuisine": "Mexican",
            "prep_time_mins": 15,
            "ingredients": [
                "1 can black beans drained",
                "2 ripe avocados sliced",
                "6 corn tortillas",
                "1/2 cup fresh salsa",
                "1/4 cup chopped cilantro",
                "1 lime cut into wedges"
            ],
            "instructions": "Warm corn tortillas on dry skillet. Mix black beans with cumin and lime juice. Assemble tacos with beans, avocado slices, salsa, and fresh cilantro.",
            "dietary_tags": ["vegan", "vegetarian", "dairy-free", "gluten-free"]
        },
        {
            "id": "recipe_3",
            "title": "Thai Green Curry Noodles",
            "cuisine": "Thai",
            "prep_time_mins": 30,
            "ingredients": [
                "200g rice noodles",
                "2 tbsp Thai green curry paste",
                "1 can coconut milk",
                "1 cup tofu cubes",
                "1 red bell pepper sliced",
                "1/2 cup fresh basil leaves"
            ],
            "instructions": "Cook rice noodles according to package. Fry green curry paste in 2 tbsp coconut milk until fragrant. Add remaining coconut milk, tofu, and bell peppers. Simmer 10 mins. Serve over noodles topped with fresh basil.",
            "dietary_tags": ["vegan", "vegetarian", "dairy-free"]
        }
    ]

    for item in recipes:
        doc_id = item["id"]
        doc_ref = collection_ref.document(doc_id)
        doc_ref.set(item)
        print(f"Seeded recipe: {item['title']} (ID: {doc_id})")

    print("Firestore seeding complete!")

if __name__ == "__main__":
    seed_database()
