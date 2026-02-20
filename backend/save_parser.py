import json
import xml.etree.ElementTree as ET

COOKING_JSON_PATH = "../xnbcli-macos/unpacked/CookingRecipes.json"
FISH_JSON_PATH = "../xnbcli-macos/unpacked/Fish.json"

# Item ID to name mapping for cooking ingredients
ITEM_NAMES = {
    "-4": "Any Fish",
    "-5": "Any Egg",
    "-6": "Any Milk",
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
    "Moss": "Moss",
}


def load_cooking_data():
    """Load cooking recipes from game data."""
    import os
    base_path = os.path.dirname(__file__)
    json_path = os.path.join(base_path, COOKING_JSON_PATH)

    with open(json_path, "r", encoding="utf8") as f:
        raw = json.load(f)

    data = raw.get("content", raw)
    recipes = {}

    for name, recipe_str in data.items():
        parts = recipe_str.strip("/").split("/")

        ing_tokens = parts[0].split()
        ingredients = []
        for i in range(0, len(ing_tokens), 2):
            item_id = ing_tokens[i]
            quantity = int(ing_tokens[i+1])
            item_name = ITEM_NAMES.get(item_id, f"Unknown ({item_id})")
            ingredients.append({"name": item_name, "quantity": quantity})

        output = 1
        recipe_id = parts[2] if len(parts) >= 3 else None

        recipes[name] = {
            "ingredients": ingredients,
            "output": output,
            "id": recipe_id
        }

    return recipes


def load_fish_data():
    """Load fish data from game data."""
    import os
    base_path = os.path.dirname(__file__)
    json_path = os.path.join(base_path, FISH_JSON_PATH)

    with open(json_path, "r", encoding="utf8") as f:
        data = json.load(f)

    fish_dict = {}
    for fish_id, fish_string in data.get("content", {}).items():
        name = fish_string.split("/")[0]
        fish_dict[fish_id] = {"name": name}

    # Add jellies that aren't in Fish.json but count for collection
    fish_dict["CaveJelly"] = {"name": "Cave Jelly"}
    fish_dict["RiverJelly"] = {"name": "River Jelly"}
    fish_dict["SeaJelly"] = {"name": "Sea Jelly"}

    return fish_dict


def parse_dict(root, path):
    """Generic dict reader from the Stardew save format."""
    result = {}
    for item in root.findall(f".//{path}/item"):
        key = item.find("./key/string")
        val = item.find("./value/int")
        if key is not None and val is not None:
            result[key.text] = int(val.text)
    return result


def get_fish_from_save(root):
    """Extract caught fish from save file."""
    fish_nodes = root.findall(".//fishCaught")

    if not fish_nodes:
        return {}

    node = next((n for n in fish_nodes if len(list(n)) > 0), None)
    if node is None:
        return {}

    fish = {}
    for item in node.findall("item"):
        key_node = item.find("./key/string")
        val_nodes = item.findall("./value/ArrayOfInt/int")

        if key_node is None or not val_nodes:
            continue

        fish_id_raw = key_node.text

        if fish_id_raw.startswith("(O)"):
            fish_id = fish_id_raw[3:]
        else:
            fish_id = fish_id_raw

        caught = int(val_nodes[0].text)
        fish[fish_id] = caught

    return fish


def analyze_save_file(save_file_path):
    """
    Analyze a Stardew Valley save file and return missing fish and recipes.

    Args:
        save_file_path: Path to the save file

    Returns:
        dict with analysis results
    """
    root = ET.parse(save_file_path).getroot()

    # Load game data
    game_recipes = load_cooking_data()
    fish_data = load_fish_data()

    # Get player progress
    learned_recipes, cooked_recipes = parse_dict(root, "cookingRecipes"), parse_dict(root, "recipesCooked")
    caught_fish = get_fish_from_save(root)

    # Analyze cooking
    all_recipes = set(game_recipes.keys())
    learned_set = set(learned_recipes.keys())

    id_to_name = {info["id"]: name for name, info in game_recipes.items()}
    cooked_set = set()
    for fid in cooked_recipes.keys():
        if fid in id_to_name:
            cooked_set.add(id_to_name[fid])
        else:
            cooked_set.add(fid)

    missing_to_cook = sorted(all_recipes - cooked_set)
    missing_to_learn = sorted(all_recipes - learned_set)

    # Format missing recipes with ingredients
    missing_recipes_detailed = []
    for recipe_name in missing_to_cook:
        recipe_info = {
            "name": recipe_name,
            "ingredients": game_recipes[recipe_name]["ingredients"],
            "needToLearn": recipe_name in missing_to_learn
        }
        missing_recipes_detailed.append(recipe_info)

    # Analyze fish
    all_fish = set(fish_data.keys())
    caught_fish_set = set(caught_fish.keys())
    uncaught_fish = all_fish - caught_fish_set

    missing_fish_detailed = []
    for fish_id in sorted(uncaught_fish):
        fish_info = fish_data.get(fish_id)
        if fish_info:
            missing_fish_detailed.append({
                "id": fish_id,
                "name": fish_info["name"]
            })

    caught_fish_detailed = []
    for fish_id in sorted(caught_fish_set):
        fish_info = fish_data.get(fish_id)
        if fish_info:
            caught_fish_detailed.append({
                "id": fish_id,
                "name": fish_info["name"]
            })

    cooked_list = [{"name": name} for name in sorted(cooked_set)]

    return {
        "recipes": {
            "total": len(all_recipes),
            "learned": len(learned_set),
            "cooked": len(cooked_set),
            "missingToLearn": len(missing_to_learn),
            "missingToCook": len(missing_to_cook),
            "missingList": missing_recipes_detailed,
            "cookedList": cooked_list,
        },
        "fish": {
            "total": len(all_fish),
            "caught": len(caught_fish_set),
            "uncaught": len(uncaught_fish),
            "missingList": missing_fish_detailed,
            "caughtList": caught_fish_detailed,
        }
    }
