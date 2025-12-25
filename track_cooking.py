import json
import xml.etree.ElementTree as ET

COOKING_JSON_PATH = "xnbcli-macos/unpacked/CookingRecipes.json"

# Item ID to name mapping for cooking ingredients (hardcoded since I can't figure out how to map IDs otherwise)
ITEM_NAMES = {
    # Category codes
    "-4": "Any Fish",
    "-5": "Any Egg",
    "-6": "Any Milk",
    # Crops
    "16": "Wild Horseradish",
    "20": "Leek",
    "22": "Dandelion",
    "24": "Parsnip",
    "78": "Cave Carrot",
    "88": "Coconut",
    "91": "Banana",
    "130": "Tuna",
    "131": "Sardine",
    "132": "Bream",
    "136": "Largemouth Bass",
    "138": "Rainbow Trout",
    "139": "Salmon",
    "142": "Carp",
    "145": "Sunfish",
    "148": "Eel",
    "151": "Squid",
    "152": "Seaweed",
    "153": "Green Algae",
    "154": "Sea Cucumber",
    "157": "White Algae",
    "188": "Green Bean",
    "190": "Cauliflower",
    "192": "Potato",
    "194": "Fried Egg",
    "216": "Bread",
    "229": "Tortilla",
    "245": "Sugar",
    "246": "Wheat Flour",
    "247": "Oil",
    "248": "Garlic",
    "250": "Kale",
    "252": "Rhubarb",
    "254": "Melon",
    "256": "Tomato",
    "257": "Morel",
    "258": "Blueberry",
    "259": "Fiddlehead Fern",
    "260": "Hot Pepper",
    "264": "Radish",
    "266": "Red Cabbage",
    "267": "Flounder",
    "269": "Midnight Carp",
    "270": "Corn",
    "272": "Eggplant",
    "274": "Artichoke",
    "276": "Pumpkin",
    "278": "Bok Choy",
    "280": "Yam",
    "282": "Cranberries",
    "284": "Beet",
    "300": "Amaranth",
    "306": "Mayonnaise",
    "308": "Void Egg",
    "372": "Clam",
    "376": "Poppy",
    "395": "Coffee",
    "404": "Common Mushroom",
    "406": "Wild Plum",
    "408": "Hazelnut",
    "410": "Blackberry",
    "412": "Winter Root",
    "419": "Vinegar",
    "423": "Rice",
    "424": "Cheese",
    "597": "Blue Jazz",
    "613": "Apple",
    "634": "Apricot",
    "715": "Lobster",
    "716": "Crayfish",
    "717": "Crab",
    "719": "Mussel",
    "720": "Shrimp",
    "721": "Snail",
    "722": "Periwinkle",
    "724": "Maple Syrup",
    "814": "Squid Ink",
    "829": "Ginger",
    "830": "Taro Root",
    "832": "Pineapple",
    "834": "Mango",
    # Named items
    "Moss": "Moss",
}

# -------- LOAD GAME COOKING DATA -------- #

def load_cooking_data():
    with open(COOKING_JSON_PATH, "r", encoding="utf8") as f:
        raw = json.load(f)

    data = raw.get("content", raw)
    recipes = {}

    for name, recipe_str in data.items():
        parts = recipe_str.strip("/").split("/")

        # Ingredient parsing (unchanged)
        ing_tokens = parts[0].split()
        ingredients = []
        for i in range(0, len(ing_tokens), 2):
            ingredients.append((ing_tokens[i], int(ing_tokens[i+1])))

        # Cooking output always 1
        output = 1

        # Recipe ID (index 2)
        recipe_id = parts[2] if len(parts) >= 3 else None

        recipes[name] = {
            "ingredients": ingredients,
            "output": output,
            "id": recipe_id
        }

    return recipes

# -------- PARSE SAVE FILE -------- #

def parse_dict(root, path):
    """Generic dict reader from the Stardew save format."""
    result = {}
    for item in root.findall(f".//{path}/item"):
        key = item.find("./key/string")
        val = item.find("./value/int")
        if key is not None and val is not None:
            result[key.text] = int(val.text)
    return result


def get_cooking_progress(save_path):
    root = ET.parse(save_path).getroot()
    learned = parse_dict(root, "cookingRecipes")
    cooked = parse_dict(root, "recipesCooked")
    return learned, cooked

def get_ingredients(recipe):
    recipes = load_cooking_data()
    if recipe in recipes:
        ingredients = recipes[recipe]["ingredients"]
        # Convert IDs to names
        named_ingredients = []
        for item_id, quantity in ingredients:
            name = ITEM_NAMES.get(item_id, f"Unknown ({item_id})")
            named_ingredients.append((name, quantity))
        return named_ingredients
    return None

# -------- MAIN -------- #

def main():
    save = "/Users/ellistonhowells/.config/StardewValley/Saves/Stickle_378934330/Stickle_378934330"
    root = ET.parse(save).getroot()
    
    game_recipes = load_cooking_data()
    learned, cooked = get_cooking_progress(save)

    all_recipes = set(game_recipes.keys())
    learned_set = set(learned.keys())
    id_to_name = {info["id"]: name for name, info in game_recipes.items()}

    # Convert cooked recipe IDs to recipe names
    cooked_set = set()

    for fid in cooked.keys():
        # Try to match numeric recipe IDs
        if fid in id_to_name:
            cooked_set.add(id_to_name[fid])
        else:
            # fallback for named keys (MossSoup etc)
            cooked_set.add(fid)

    missing_cooked = sorted(all_recipes - cooked_set)
    missing_learned = sorted(all_recipes - learned_set)

    print("\n==== Summary ====")
    print("Total recipes in game:", len(all_recipes))
    print("Learned:", len(learned_set))
    print("Cooked:", len(cooked_set))
    print("Need to learn:", len(missing_learned))
    print("Need to cook:", len(missing_cooked))

    print("\n=== Ingredients ===")
    for food in missing_cooked:
        if food in missing_learned:
            print(f'{food}: {get_ingredients(food)} **NEED TO LEARN')
        else: 
            print(f'{food}: {get_ingredients(food)}')

if __name__ == '__main__':
    main()
