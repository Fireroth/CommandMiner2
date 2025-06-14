import globalHandler
import json

def load_config():
    config_path = "./data/config.json"

    try:
        with open(config_path, "r") as file:
            config_data = json.load(file)

        globalHandler.colorsName = config_data.get("colorsName", "")
        globalHandler.sepChar = config_data.get("sepChar", "|")
        globalHandler.output_font_size = config_data.get("output_font_size", "12")
        globalHandler.auto_focus = config_data.get("auto_focus", True)
        globalHandler.autoSave = config_data.get("autoSave", False)
        globalHandler.exitWarn = config_data.get("exitWarn", True)
        globalHandler.mod_support = config_data.get("mod_support", False)
        globalHandler.accs_support = config_data.get("accs_support", False)

        for key, value in config_data.items():
            print(f"[IOHandler][Config][Read] {key}: {value}")

    except FileNotFoundError:
        print(f"The config file '{config_path}' was not found.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from '{config_path}'.")
        

def save_config():
    config_data = {
        "colorsName": globalHandler.colorsName,
        "sepChar": globalHandler.sepChar,
        "output_font_size": globalHandler.output_font_size,
        "auto_focus": globalHandler.auto_focus,
        "autoSave": globalHandler.autoSave,
        "exitWarn": globalHandler.exitWarn,
        "mod_support": globalHandler.mod_support,
        "accs_support": globalHandler.accs_support
    }

    try:
        with open("./data/config.json", "w") as file:
            json.dump(config_data, file, indent=4)

        for key, value in config_data.items():
            print(f"[IOHandler][Config][Write] {key}: {value}")

    except IOError:
        print("Error writing to the 'config.json' file.")


def load_save():
    save_path = f"./data/save_{globalHandler.account}.json"

    try:
        with open(save_path, "r") as file:
            save_data = json.load(file)

        globalHandler.money = save_data.get("money", 0)
        globalHandler.ore_amount = save_data.get("ore_amount", 0)
        globalHandler.pickaxe_level = save_data.get("pickaxe_level", 1)
        globalHandler.backpack_capacity = save_data.get("backpack_capacity", 0)
        globalHandler.backpack_level = save_data.get("backpack_level", 1)
        globalHandler.tokens = save_data.get("tokens", 0)
        globalHandler.ore_multiplier = save_data.get("ore_multiplier", 1)
        globalHandler.common_crate = save_data.get("common_crate", 0)
        globalHandler.uncommon_crate = save_data.get("uncommon_crate", 0)
        globalHandler.rare_crate = save_data.get("rare_crate", 0)
        globalHandler.epic_crate = save_data.get("epic_crate", 0)
        globalHandler.legendary_crate = save_data.get("legendary_crate", 0)
        globalHandler.autosell = save_data.get("autosell", 0)
        globalHandler.rebirth_token_reward = save_data.get("rebirth_token_reward", 0)
        globalHandler.rebirth_amount = save_data.get("rebirth_amount", 0)
        globalHandler.minimum_mined = save_data.get("minimum_mined", 0)
        globalHandler.auto_crate_open = save_data.get("auto_crate_open", 0)
        globalHandler.double_mine = save_data.get("double_mine", 0)

        for key, value in save_data.items():
            print(f"[IOHandler][Save][Read] {key}: {value}")

        globalHandler.saveLoaded = True

    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON in '{save_path}'.")
    except FileNotFoundError:
        print("File was not found.")
    except Exception as e:
        print(f"An unexpected error occurred while loading: {e}")


def save_progress(silent=False):
    save_data = {
        "money": globalHandler.money,
        "ore_amount": globalHandler.ore_amount,
        "pickaxe_level": globalHandler.pickaxe_level,
        "backpack_capacity": globalHandler.backpack_capacity,
        "backpack_level": globalHandler.backpack_level,
        "tokens": globalHandler.tokens,
        "ore_multiplier": globalHandler.ore_multiplier,
        "common_crate": globalHandler.common_crate,
        "uncommon_crate": globalHandler.uncommon_crate,
        "rare_crate": globalHandler.rare_crate,
        "epic_crate": globalHandler.epic_crate,
        "legendary_crate": globalHandler.legendary_crate,
        "autosell": globalHandler.autosell,
        "rebirth_token_reward": globalHandler.rebirth_token_reward,
        "rebirth_amount": globalHandler.rebirth_amount,
        "minimum_mined": globalHandler.minimum_mined,
        "auto_crate_open": globalHandler.auto_crate_open,
        "double_mine": globalHandler.double_mine
    }

    save_path = f"./data/save_{globalHandler.account}.json"

    try:
        with open(save_path, "w") as file:
            json.dump(save_data, file, indent=4)

        if not silent:
            for key, value in save_data.items():
                print(f"[IOHandler][Save][Write] {key}: {value}")

    except IOError:
        print(f"Error writing to '{save_path}' file.")


def load_theme():
    try:
        with open(f"./data/colorScheme_{globalHandler.colorsName}.json", "r") as file:
            theme = json.load(file)

            globalHandler.globalBg = theme.get("globalBg", "")
            globalHandler.consoleBg = theme.get("consoleBg", "")
            globalHandler.buttonBg = theme.get("buttonBg", "")
            globalHandler.entryBg = theme.get("entryBg", "")
            globalHandler.titleFg = theme.get("titleFg", "")
            globalHandler.buttonFg = theme.get("buttonFg", "")

            globalHandler.redColor = theme.get("redColor", "")
            globalHandler.lightRedColor = theme.get("lightRedColor", "")
            globalHandler.darkRedColor = theme.get("darkRedColor", "")
            globalHandler.pinkColor = theme.get("pinkColor", "")
            globalHandler.orangeColor = theme.get("orangeColor", "")
            globalHandler.lightOrangeColor = theme.get("lightOrangeColor", "")
            globalHandler.darkOrangeColor = theme.get("darkOrangeColor", "")
            globalHandler.yellowColor = theme.get("yellowColor", "")
            globalHandler.lightYellowColor = theme.get("lightYellowColor", "")
            globalHandler.darkYellowColor = theme.get("darkYellowColor", "")
            globalHandler.greenColor = theme.get("greenColor", "")
            globalHandler.lightGreenColor = theme.get("lightGreenColor", "")
            globalHandler.darkGreenColor = theme.get("darkGreenColor", "")
            globalHandler.limeColor = theme.get("limeColor", "")
            globalHandler.blueColor = theme.get("blueColor", "")
            globalHandler.lightBlueColor = theme.get("lightBlueColor", "")
            globalHandler.darkBlueColor = theme.get("darkBlueColor", "")
            globalHandler.cyanColor = theme.get("cyanColor", "")
            globalHandler.whiteColor = theme.get("whiteColor", "")
            globalHandler.greyColor = theme.get("greyColor", "")
            globalHandler.blackColor = theme.get("blackColor", "")
            globalHandler.purpleColor = theme.get("purpleColor", "")
            globalHandler.lightGreyColor = theme.get("lightGreyColor", "")

    except FileNotFoundError:
        print(f"The 'colorScheme_{globalHandler.colorsName}.json' file was not found.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON in 'colorScheme_{globalHandler.colorsName}.json'.")


if __name__ == "__main__":
    print("Run Launcher.pyw or main.py")
    _ = input("Press Enter to exit...")

else:
    print("[Import] IOHandler imported as module")
