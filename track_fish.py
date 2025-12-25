import json
import xml.etree.ElementTree as ET

FISH_JSON_PATH = "xnbcli-macos/unpacked/Fish.json" 

def load_fish_data():
    with open(FISH_JSON_PATH, "r", encoding="utf8") as f:
        data = json.load(f)
    # Extract content and parse fish names from the string format
    fish_dict = {}
    for fish_id, fish_string in data.get("content", {}).items():
        # Format: "Name/difficulty/behavior/..." - name is first segment
        name = fish_string.split("/")[0]
        fish_dict[fish_id] = {"Name": name}
    return fish_dict

def get_fish_species(save_path):
    root = ET.parse(save_path).getroot()
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

        # Strip "(O)" prefix for numeric fish IDs
        if fish_id_raw.startswith("(O)"):
            fish_id = fish_id_raw[3:]  # keep as string, no int conversion
        else:
            fish_id = fish_id_raw

        caught = int(val_nodes[0].text)
        fish[fish_id] = caught

    return fish


def main():
    save = "/Users/ellistonhowells/.config/StardewValley/Saves/Stickle_378934330/Stickle_378934330"
    fish_data = load_fish_data()
    caught = get_fish_species(save)

    if not caught:
        print("No fish species recorded in save.")
        return

    # Convert to sets for easy comparison
    all_fish = set(fish_data.keys())
    caught_fish = set(caught.keys())
    uncaught_fish = all_fish - caught_fish

    print(f"\nDistinct species caught: {len(caught_fish)}")
    print(f"Total fish caught: {sum(caught.values())}")
    print(f"Uncaught species: {len(uncaught_fish)}\n")

    print("=== CAUGHT ===")
    for fid in sorted(caught_fish):
        info = fish_data.get(str(fid))
        name = info.get("Name") if info else f"{fid}"
        print(f"{name} → {caught[fid]} times")

    print("\n=== UNCAUGHT ===")
    for fid in sorted(uncaught_fish):
        info = fish_data.get(str(fid))
        name = info.get("Name") if info else f"Unknown ({fid})"
        print(name)


if __name__ == "__main__":
    main()


# Path to save:
# /Users/ellistonhowells/.config/StardewValley/Saves/Stickle_378934330/Stickle_378934330

# To find game data:
# /Users/ellistonhowells/Library/Application Support/Steam/steamapps/common/Stardew Valley/Contents/Resources/Content/Data