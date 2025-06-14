import tkinter as tk
import os
import importlib.util
import globalHandler
import IOHandler
from tkinter import scrolledtext, messagebox, ttk
from random import randint
from settings import settingsWindow
from accountHandler import accWindow
from inspect import signature


def load_mods():

    if not os.path.exists("mods"):
        os.makedirs("mods")
        print('Folder "mods" created.')
        return
    
    for filename in os.listdir("mods"):
        if filename.endswith(".py"):
            mod_path = os.path.join("mods", filename)
            mod_name = filename[:-3]
            globalHandler.mod_list += (f"{mod_name}\n")
            
            spec = importlib.util.spec_from_file_location(mod_name, mod_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            try:
                for functionName in mod.load_functions:
                    load = f"mod.{functionName} = {functionName}"
                    exec(load)
            except AttributeError:
                print(f"[Mods][Warn] 'load_functions' was not found in {mod_name}")

            try:
                mod.init()
            except AttributeError:
                print(f"[Mods][Warn] 'init()' function was not found in {mod_name}")

            for attr_name in dir(mod):
                attr = getattr(mod, attr_name)
                if callable(attr) and str(signature(attr).parameters.get("executable")) == "executable=True":
                    command_name = str(signature(attr).parameters.get("command").default)
                    globalHandler.function_mod_dict[command_name] = attr
                    globalHandler.mod_commands += f"{command_name}\n"
                    print(f"[Mods][Load] '{mod_name}' loaded function '{attr_name}' accessible with command '{command_name}'")


def update_top_label():
    global pickaxe_icon, ore_icon
    name_generator()
    money_label.config(text=f"Money: {globalHandler.money}")
    tokens_label.config(text=f"Tokens: {globalHandler.tokens}")

    if globalHandler.ore_multiplier >= 11:
        ore_icon = tk.PhotoImage(file="./images/bedrock.png")
    else:
        ore_icon = tk.PhotoImage(file=ore_icons[globalHandler.ore_name])
    ore_label.config(image=ore_icon)

    pickaxe_icon = tk.PhotoImage(file=pickaxe_icons[globalHandler.pickaxe_name])
    pickaxe_label.config(image=pickaxe_icon)

    backpack_label.config(text=f"Backpack: {globalHandler.ore_amount}/{globalHandler.backpack_capacity}")
    pickaxe_label.config(text=f"Pickaxe level: {globalHandler.pickaxe_level}")
    ore_label.config(text=f"Ore: {globalHandler.ore_name}")


def process_input():
    user_input = entry.get().lower()
    entry.delete(0, "end")

    if user_input and (not globalHandler.input_history or user_input != globalHandler.input_history[-1]):
        globalHandler.input_history.append(user_input)
        print("[Main][Input_History] Submitted", user_input, "to input history")
    globalHandler.history_index = len(globalHandler.input_history)

    if user_input == "" or user_input == placeholder_text.lower():
        add_output("[Error] ", globalHandler.lightRedColor, "Empty command!", globalHandler.redColor)
    elif user_input in globalHandler.function_mod_dict:
        try:
            globalHandler.function_mod_dict[user_input]()
        except Exception as err:
            add_output("[Error] ", globalHandler.lightRedColor, f"Command '{user_input}' failed: {err}", globalHandler.redColor)
    elif user_input in function_dict:
        try:
            exec(function_dict[user_input])
        except Exception as err:
            add_output("[Error] ", globalHandler.lightRedColor, f"Command '{user_input}' failed: {err}", globalHandler.redColor)
    else:
        add_output("[Error] ", globalHandler.lightRedColor, "Command ", globalHandler.redColor, user_input, globalHandler.redColor, " does not exist", globalHandler.redColor)

    if globalHandler.sepChar == "Empty line":
        add_output("", "")
    elif globalHandler.sepChar == "----------":
        add_output("------------------------------------------------------------------", "")

    if globalHandler.autoSave:
        save_progress("silent")


def mine_ore(repeat=0):
    if globalHandler.minimum_mined == 0 and randint(1, 5) == 1:
        mined_amount = 0
    else:
        mined_amount = max(randint(1, 5) * globalHandler.pickaxe_level + randint(0, 4), globalHandler.minimum_mined)

    if globalHandler.ore_amount + mined_amount < globalHandler.backpack_capacity:
        crate_chances = [
            (1000, 980, "common_crate", "Common", (10, 200), 150, globalHandler.whiteColor),
            (1700, 1690, "uncommon_crate", "Uncommon", (30, 400), 365, globalHandler.lightGreenColor),
            (3000, 2990, "rare_crate", "Rare", (70, 625), 620, globalHandler.lightBlueColor),
            (5000, 4996, "epic_crate", "Epic", (165, 925), 924, globalHandler.purpleColor),
            (7500, 7499, "legendary_crate", "Legendary", (290, 1300), 1999, globalHandler.yellowColor)]
        
        for max_val, threshold, var_name, crate_name, reward_range, unlucky_threshold, color in crate_chances:
            random_value = randint(1, max_val)
            if random_value >= threshold:
                setattr(globalHandler, var_name, getattr(globalHandler, var_name) + 1)
                add_output(f"You obtained 1 {crate_name.lower()} crate", color)
                if globalHandler.auto_crate_open:
                    open_crate(crate_name=crate_name, crate_var_name=var_name, reward_range=reward_range, unlucky_threshold=unlucky_threshold, reward_color=color)
                break

        globalHandler.ore_amount += mined_amount
        add_output(f"You mined {mined_amount} units of {globalHandler.ore_name}. Total ore in backpack: {globalHandler.ore_amount}",globalHandler.lightGreyColor,)
    elif globalHandler.ore_amount == globalHandler.backpack_capacity:
        if globalHandler.autosell:
            sell_ore()
        else:
            add_output("Backpack is full. Sell some ore or free up space in backpack.", globalHandler.redColor)
    else:
        globalHandler.ore_amount = globalHandler.backpack_capacity
        add_output(f"You mined {mined_amount} units of {globalHandler.ore_name}. Total ore in backpack: {globalHandler.ore_amount}",globalHandler.lightGreyColor,)

    update_top_label()

    if globalHandler.double_mine and repeat == 0 and globalHandler.ore_amount < globalHandler.backpack_capacity:
        mine_ore(repeat=1)


def sell_ore():
    if globalHandler.ore_amount > 0:
        sale_amount = globalHandler.ore_amount * globalHandler.ore_multiplier
        globalHandler.money += sale_amount
        add_output(f"You sold {globalHandler.ore_amount} {globalHandler.ore_name} for {sale_amount}$. Total money: {globalHandler.money}", globalHandler.lightGreenColor)
        globalHandler.ore_amount = 0
    else:
        add_output("[Error] ", globalHandler.lightRedColor, f"You have no {globalHandler.ore_name} to sell.", globalHandler.redColor)
    update_top_label()


def upgrade_pickaxe():
    global pickaxe_price
    if globalHandler.money >= pickaxe_price:
        globalHandler.money -= pickaxe_price
        globalHandler.pickaxe_level += 1
        pickaxe_price = globalHandler.pickaxe_level*200
        add_output(f"You upgraded the pickaxe to level {globalHandler.pickaxe_level}. New upgrade price: {pickaxe_price}$.", globalHandler.lightBlueColor)
    else:
        add_output("[Error] ", globalHandler.lightRedColor, f"Not enough money to upgrade the pickaxe. Next upgrade cost {pickaxe_price}$.", globalHandler.redColor)
    update_top_label()


def upgrade_backpack():
    global backpack_upgrade_cost
    if globalHandler.money >= backpack_upgrade_cost:
        globalHandler.money -= backpack_upgrade_cost
        globalHandler.backpack_level += 1
        globalHandler.backpack_capacity += 25
        backpack_upgrade_cost = globalHandler.backpack_capacity*2
        add_output(f"You increased backpack capacity to {globalHandler.backpack_capacity}. New upgrade price: {backpack_upgrade_cost}$.", globalHandler.lightBlueColor)
    else:
        add_output("[Error] ", globalHandler.lightRedColor, f"Not enough money to increase backpack capacity. Next upgrade cost {backpack_upgrade_cost}$.", globalHandler.redColor)
    update_top_label()


def upgrade_ore():
    global ore_upgrade_cost
    if globalHandler.tokens >= ore_upgrade_cost:
        globalHandler.tokens -= ore_upgrade_cost
        globalHandler.ore_multiplier +=1
        ore_upgrade_cost = ore_upgrade_cost+2
        globalHandler.ore_amount = 0
        update_top_label()
        add_output(f"You increased ore to {globalHandler.ore_name}. New upgrade price: {ore_upgrade_cost} tokens.", globalHandler.lightBlueColor)
    else:
        add_output("[Error] ", globalHandler.lightRedColor, f"Not enough tokens to increase ore. Next upgrade cost {ore_upgrade_cost} tokens.", globalHandler.redColor)


def open_crate(crate_name, crate_var_name, reward_range, unlucky_threshold, reward_color):
    #common     (crate_name="Common", crate_var_name="common_crate", reward_range=(10, 200), unlucky_threshold=150, reward_color=globalHandler.whiteColor)
    #uncommon   (crate_name="Uncommon", crate_var_name="uncommon_crate", reward_range=(30, 400), unlucky_threshold=365, reward_color=globalHandler.lightGreenColor)
    #rare       (crate_name="Rare", crate_var_name="rare_crate", reward_range=(70, 625), unlucky_threshold=620, reward_color=globalHandler.lightBlueColor)
    #epic       (crate_name="Epic", crate_var_name="epic_crate", reward_range=(165, 925), unlucky_threshold=924, reward_color=globalHandler.purpleColor)
    #legendary  (crate_name="Legendary", crate_var_name="legendary_crate", reward_range=(230, 1300), unlucky_threshold=1999, reward_color=globalHandler.yellowColor)
    crate_count = getattr(globalHandler, crate_var_name)
    if crate_count <= 0:
        add_output(f"You have no {crate_name} crates to open.", globalHandler.redColor)
    else:
        setattr(globalHandler, crate_var_name, crate_count - 1)

        crateMoney = randint(*reward_range)
        if crateMoney > unlucky_threshold:
            crateMoney = 0
            add_output(f"You got {crateMoney}$ from {crate_name} crate", globalHandler.redColor)
            add_output(f"Sorry but you got unlucky this time :(", globalHandler.redColor)
        else:
            globalHandler.money += crateMoney
            add_output(f"You got {crateMoney}$ from {crate_name} crate", reward_color)
    update_top_label()


def open_crate_all():
    while globalHandler.common_crate != 0:
        open_crate(crate_name="Common", crate_var_name="common_crate", reward_range=(10, 200), unlucky_threshold=150, reward_color=globalHandler.whiteColor)
    while globalHandler.uncommon_crate != 0:
        open_crate(crate_name="Uncommon", crate_var_name="uncommon_crate", reward_range=(30, 400), unlucky_threshold=365, reward_color=globalHandler.lightGreenColor)
    while globalHandler.rare_crate != 0:
        open_crate(crate_name="Rare", crate_var_name="rare_crate", reward_range=(70, 625), unlucky_threshold=620, reward_color=globalHandler.lightBlueColor)
    while globalHandler.epic_crate != 0:
        open_crate(crate_name="Epic", crate_var_name="epic_crate", reward_range=(165, 925), unlucky_threshold=924, reward_color=globalHandler.purpleColor)
    while globalHandler.legendary_crate != 0:
        open_crate(crate_name="Legendary", crate_var_name="legendary_crate", reward_range=(230, 1300), unlucky_threshold=1999, reward_color=globalHandler.yellowColor)

    add_output("All crates have been opened", globalHandler.lightGreenColor)


def stats():
    add_output("Money: ", globalHandler.lightGreenColor, f"{globalHandler.money}$", globalHandler.whiteColor,
    "\nTokens: ", globalHandler.lightGreenColor, globalHandler.tokens, globalHandler.whiteColor,
    "\nRebirth count: ", globalHandler.lightGreenColor, globalHandler.rebirth_amount, globalHandler.whiteColor,
    "\nPickaxe level: ", globalHandler.lightBlueColor, globalHandler.pickaxe_level, globalHandler.whiteColor,
    "\nPickaxe max mine: ", globalHandler.lightBlueColor, globalHandler.pickaxe_level*5+4, globalHandler.whiteColor,
    "\nPickaxe upgrade price: ", globalHandler.lightBlueColor, f"{pickaxe_price}$", globalHandler.whiteColor,
    "\nPickaxe name: ", globalHandler.lightBlueColor, globalHandler.pickaxe_name, globalHandler.whiteColor,
    "\nBackpack size: ", globalHandler.lightOrangeColor, globalHandler.backpack_capacity, globalHandler.whiteColor,
    "\nBackpack level: ", globalHandler.lightOrangeColor, globalHandler.backpack_level, globalHandler.whiteColor,
    "\nBackpack upgrade price: ", globalHandler.lightOrangeColor, f"{backpack_upgrade_cost}$", globalHandler.whiteColor,
    "\nBackpack name: ", globalHandler.lightOrangeColor, globalHandler.backpack_name, globalHandler.whiteColor,
    f"\nOre multiplier: {globalHandler.ore_multiplier}", globalHandler.whiteColor,
    f"\nOre name: {globalHandler.ore_name}", globalHandler.whiteColor,
    f"\nOre amount in BP: {globalHandler.ore_amount}", globalHandler.whiteColor,
    f"\nOre upgrade price: {ore_upgrade_cost} tokens", globalHandler.whiteColor)
    

def allCrates():
    add_output("Common: ", globalHandler.whiteColor, globalHandler.common_crate, globalHandler.whiteColor,
    "\nUncommon: ", globalHandler.lightGreenColor, globalHandler.uncommon_crate, globalHandler.whiteColor,
    "\nRare: ", globalHandler.lightBlueColor, globalHandler.rare_crate, globalHandler.whiteColor,
    "\nEpic: ", globalHandler.purpleColor, globalHandler.epic_crate, globalHandler.whiteColor,
    "\nLegendary: ", globalHandler.yellowColor, globalHandler.legendary_crate, globalHandler.whiteColor)


def help_page(mode = "default"):
    add_output("Available commands:", globalHandler.blueColor)
    if mode == "dev":
        for command, description in available_commands_dev.items():
            add_output("|| ", globalHandler.lightBlueColor, f"{command}: {description}", globalHandler.whiteColor)
    else:
        for command, description in available_commands.items():
            add_output("|| ", globalHandler.lightBlueColor, f"{command}: {description}", globalHandler.whiteColor)
        if globalHandler.mod_support:
            add_output("|| ", globalHandler.lightRedColor, "help mods: See all commands added by mods", globalHandler.whiteColor)
            add_output("|| ", globalHandler.lightRedColor, "mods: See all loaded mods", globalHandler.whiteColor)
        if globalHandler.accs_support:
            add_output("|| ", globalHandler.lightRedColor, "accs: Open account manager", globalHandler.whiteColor)
        add_output("[Note] ", globalHandler.blueColor, "There is a lot of aliases like ", globalHandler.whiteColor, "o l ", globalHandler.lightYellowColor, 
                   "for ", globalHandler.whiteColor, "open legendary ", globalHandler.lightYellowColor, "and many more", globalHandler.whiteColor)


def token_shop():
    add_output("Autosell", globalHandler.lightGreenColor,
    "\n||", globalHandler.lightGreenColor, f" Current level: {globalHandler.autosell}", globalHandler.whiteColor,
    "\n||", globalHandler.lightGreenColor, f" Upgrade price: {autosell_next_price}", globalHandler.whiteColor,
    "\n||", globalHandler.lightGreenColor, " Upgrade command: buy autosell", globalHandler.whiteColor,
    "\n\nRebirth Token Reward", globalHandler.pinkColor,
    "\n||", globalHandler.pinkColor, f" Current rebirth reward: {globalHandler.rebirth_token_reward+1} token(s)", globalHandler.whiteColor,
    "\n||", globalHandler.pinkColor, f" Upgrade price: {rebirth_token_reward_next_price}", globalHandler.whiteColor,
    "\n||", globalHandler.pinkColor, " Upgrade command: buy rebreward", globalHandler.whiteColor,
    "\n\nMinimum Mined", globalHandler.lightOrangeColor,
    "\n||", globalHandler.lightOrangeColor, f" Current minimum mined: {globalHandler.minimum_mined} ore(s)", globalHandler.whiteColor,
    "\n||", globalHandler.lightOrangeColor, f" Upgrade price: {minimum_mined_next_price}", globalHandler.whiteColor,
    "\n||", globalHandler.lightOrangeColor, " Upgrade command: buy minmined", globalHandler.whiteColor,
    "\n\nAuto Crate Open", globalHandler.lightBlueColor,
    "\n||", globalHandler.lightBlueColor, f" Current level: {globalHandler.auto_crate_open}", globalHandler.whiteColor,
    "\n||", globalHandler.lightBlueColor, f" Upgrade price: {auto_crate_open_next_price}", globalHandler.whiteColor,
    "\n||", globalHandler.lightBlueColor, " Upgrade command: buy autocrates", globalHandler.whiteColor,
    "\n\nDouble Mining", globalHandler.lightRedColor,
    "\n||", globalHandler.lightRedColor, f" Current level: {globalHandler.double_mine}",globalHandler. whiteColor,
    "\n||", globalHandler.lightRedColor, f" Upgrade price: {double_mine_next_price}", globalHandler.whiteColor,
    "\n||", globalHandler.lightRedColor, " Upgrade command: buy doublemine", globalHandler.whiteColor)


def buy_autosell():
    global autosell_next_price
    if globalHandler.autosell == 1:
        add_output("Autosell has reached its maximum level", globalHandler.redColor)
    elif globalHandler.tokens >= autosell_next_price:
        globalHandler.tokens -= autosell_next_price
        globalHandler.autosell = 1
        add_output(f"Autosell has been upgraded to level 1 for {autosell_next_price} tokens", globalHandler.lightGreenColor)
        autosell_next_price = 0
        update_top_label()
    else:
        add_output("[Error] ", globalHandler.lightRedColor, "Not enough tokens to buy Autosell", globalHandler.redColor)


def buy_autocrates():
    global auto_crate_open_next_price
    if globalHandler.auto_crate_open == 1:
        add_output("Auto crate open has reached its maximum level", globalHandler.redColor)
    elif globalHandler.tokens >= auto_crate_open_next_price:
        globalHandler.tokens -= auto_crate_open_next_price
        globalHandler.auto_crate_open = 1
        add_output(f"Auto crate open has been upgraded to level 1 for {auto_crate_open_next_price} tokens", globalHandler.lightGreenColor)
        auto_crate_open_next_price = 0
        update_top_label()
    else:
        add_output("[Error] ", globalHandler.lightRedColor, "Not enough tokens to buy Auto crate open", globalHandler.redColor)


def buy_doublemine():
    global double_mine_next_price
    if globalHandler.double_mine == 1:
        add_output("Double mine has reached its maximum level", globalHandler.redColor)
    elif globalHandler.tokens >= double_mine_next_price:
        globalHandler.tokens -= double_mine_next_price
        globalHandler.double_mine = 1
        add_output(f"Double mine has been upgraded to level 1 for {double_mine_next_price} tokens", globalHandler.lightGreenColor)
        double_mine_next_price = 0
        update_top_label()
    else:
        add_output("[Error] ", globalHandler.lightRedColor, "Not enough tokens to buy Double mine", globalHandler.redColor)


def buy_rebreward():
    global rebirth_token_reward_next_price
    if globalHandler.rebirth_token_reward == 1:
        add_output("Rebirth token reward has reached its maximum level", globalHandler.redColor)
    elif globalHandler.tokens >= rebirth_token_reward_next_price:
        globalHandler.tokens -= rebirth_token_reward_next_price
        globalHandler.rebirth_token_reward = 1
        add_output(f"Rebirth token reward has been upgraded to level 1 for {rebirth_token_reward_next_price} tokens", globalHandler.lightGreenColor)
        rebirth_token_reward_next_price = 0
        update_top_label()
    else:
        add_output("[Error] ", globalHandler.lightRedColor, "Not enough tokens to buy Rebirth token reward", globalHandler.redColor)


def buy_minmined():
    global minimum_mined_next_price
    if globalHandler.tokens >= minimum_mined_next_price:
        globalHandler.tokens -= minimum_mined_next_price
        globalHandler.minimum_mined += 1
        add_output(f"Rebirth token reward has been upgraded to level {globalHandler.minimum_mined} for {minimum_mined_next_price} tokens", globalHandler.lightGreenColor)
        minimum_mined_next_price += 1
        update_top_label()
    else:
        add_output("[Error] ", globalHandler.lightRedColor, "Not enough tokens to buy Minimum mined", globalHandler.redColor)


def save_progress(mode = "normal"): 
        
        if mode == "silent":
            IOHandler.save_progress(silent = True)
        elif mode == "normal" and globalHandler.autoSave:
            add_output("AutoSaving is enabled\nNo need to run this command", globalHandler.greenColor)
        elif mode == "normal":
            IOHandler.save_progress()
            add_output("Saving was successful.", globalHandler.greenColor)


def reset_progress():
    reset_confirm = messagebox.askyesno("Are you sure?", "Are you sure you want to reset your progress?")
    print(f"[Main] messagebox.askyesno (reset_confirm): {reset_confirm}")
    if reset_confirm == False:
        add_output("Reset was aborted", globalHandler.lightRedColor)
        return
    
    globalHandler.money = 0
    globalHandler.pickaxe_level = 1
    globalHandler.backpack_capacity = 50
    globalHandler.backpack_level = 1
    globalHandler.ore_amount = 0
    globalHandler.tokens = 0
    globalHandler.ore_multiplier = 1
    globalHandler.common_crate = 0
    globalHandler.uncommon_crate = 0
    globalHandler.rare_crate = 0
    globalHandler.epic_crate = 0
    globalHandler.legendary_crate = 0
    globalHandler.autosell = 0
    globalHandler.rebirth_token_reward = 0
    globalHandler.rebirth_amount = 0
    globalHandler.minimum_mined = 0
    globalHandler.auto_crate_open = 0
    globalHandler.double_mine = 0
    update_prices()
    update_top_label()
    add_output("Reset was successful.", globalHandler.lightGreenColor)


def update_prices():
    global pickaxe_price, backpack_upgrade_cost, ore_upgrade_cost, auto_crate_open_next_price, autosell_next_price
    global double_mine_next_price, rebirth_token_reward_next_price, minimum_mined_next_price

    pickaxe_price = globalHandler.pickaxe_level*200
    backpack_upgrade_cost = globalHandler.backpack_capacity*2
    ore_upgrade_cost = globalHandler.ore_multiplier+2

    if globalHandler.auto_crate_open == 0:
        auto_crate_open_next_price = 5
    else:
        auto_crate_open_next_price = 0

    if globalHandler.autosell == 0:
        autosell_next_price = 10
    else:
        autosell_next_price = 0

    if globalHandler.double_mine == 0:
        double_mine_next_price = 10
    else:
        double_mine_next_price = 0

    if globalHandler.rebirth_token_reward == 0:
        rebirth_token_reward_next_price = 5
    else:
        rebirth_token_reward_next_price = 0

    minimum_mined_next_price = globalHandler.minimum_mined + 1


def name_generator():
    global ore_icons, pickaxe_icons
    ore_names_dict = {
        1: "Coal",
        2: "Iron",
        3: "Copper",
        4: "Lapis",
        5: "Quartz",
        6: "Gold",
        7: "Redstone",
        8: "Diamond",
        9: "Emerald",
        10: "Netherite",
        11: "Bedrock"
    }
    if globalHandler.ore_multiplier >= 12:
        globalHandler.ore_name = f"Bedrock+{globalHandler.ore_multiplier-11}"
    else:
        globalHandler.ore_name = ore_names_dict[globalHandler.ore_multiplier]

    ore_icons = {
        "Coal": "./images/coal.png",
        "Iron": "./images/iron.png",
        "Copper": "./images/copper.png",
        "Lapis": "./images/lapis.png",
        "Quartz": "./images/quartz.png",
        "Gold": "./images/gold.png",
        "Redstone": "./images/redstone.png",
        "Diamond": "./images/diamond.png",
        "Emerald": "./images/emerald.png",
        "Netherite": "./images/netherite.png",
    }

    tools_names_dict = {
        1: "Wooden",
        10: "Stone",
        20: "Copper",
        30: "Iron",
        40: "Quartz",
        50: "Golden",
        60: "Redstone",
        70: "Diamond",
        80: "Emerald",
        90: "Netherite",
        100: "Bedrock"
    }

    sorted_levels = sorted(tools_names_dict.keys())
    
    for i in range(len(sorted_levels) - 1):
        if sorted_levels[i] <= globalHandler.pickaxe_level < sorted_levels[i + 1]:
            globalHandler.pickaxe_name = tools_names_dict[sorted_levels[i]]
    
    if globalHandler.pickaxe_level >= sorted_levels[-1]:
        globalHandler.pickaxe_name =  tools_names_dict[sorted_levels[-1]]

    for i in range(len(sorted_levels) - 1):
        if sorted_levels[i] <= globalHandler.backpack_level < sorted_levels[i + 1]:
            globalHandler.backpack_name = tools_names_dict[sorted_levels[i]]
    
    if globalHandler.backpack_level >= sorted_levels[-1]:
        globalHandler.backpack_name =  tools_names_dict[sorted_levels[-1]]

    pickaxe_icons = {
        "Wooden": "./images/wooden_pickaxe.png",
        "Stone": "./images/stone_pickaxe.png",
        "Copper": "./images/copper_pickaxe.png",
        "Iron": "./images/iron_pickaxe.png",
        "Quartz": "./images/quartz_pickaxe.png",
        "Golden": "./images/gold_pickaxe.png",
        "Redstone": "./images/redstone_pickaxe.png",
        "Diamond": "./images/diamond_pickaxe.png",
        "Emerald": "./images/emerald_pickaxe.png",
        "Netherite": "./images/netherite_pickaxe.png",
        "Bedrock": "./images/bedrock_pickaxe.png"
    }


def rebirth():
    if globalHandler.pickaxe_level >= 100:
        globalHandler.pickaxe_level = 1
        globalHandler.backpack_capacity = 50
        globalHandler.money = 0
        globalHandler.ore_amount = 0
        globalHandler.common_crate = 0
        globalHandler.uncommon_crate = 0
        globalHandler.rare_crate = 0
        globalHandler.epic_crate = 0
        globalHandler.legendary_crate = 0

        globalHandler.tokens += 1 + globalHandler.rebirth_token_reward
        add_output("Rebirth was successful. +", globalHandler.lightGreenColor, 1 + globalHandler.rebirth_token_reward, globalHandler.lightGreenColor,  " Token(s)", globalHandler.lightGreenColor)
        globalHandler.rebirth_amount += 1
        update_top_label()
    else:
        add_output("[Error] ", globalHandler.lightRedColor, "Failed to rebirth you need pickaxe level 100 or higher.", globalHandler.redColor)


def colorOutputTest():
    colorBlock = "████████▓▓▓▓▓▓▓▓▒▒▒▒▒▒▒▒░░░░░░░░"
    add_output(f"{colorBlock} redColor", globalHandler.redColor,
    f"\n{colorBlock} lightRedColor", globalHandler.lightRedColor,
    f"\n{colorBlock} darkRedColor", globalHandler.darkRedColor,
    f"\n{colorBlock} pinkColor", globalHandler.pinkColor,
    f"\n{colorBlock} orangeColor", globalHandler.orangeColor,
    f"\n{colorBlock} lightOrangeColor", globalHandler.lightOrangeColor,
    f"\n{colorBlock} darkOrangeColor", globalHandler.darkOrangeColor,
    f"\n{colorBlock} yellowColor", globalHandler.yellowColor,
    f"\n{colorBlock} lightYellowColor", globalHandler.lightYellowColor,
    f"\n{colorBlock} darkYellowColor", globalHandler.darkYellowColor,
    f"\n{colorBlock} greenColor", globalHandler.greenColor,
    f"\n{colorBlock} lightGreenColor", globalHandler.lightGreenColor,
    f"\n{colorBlock} darkGreenColor", globalHandler.darkGreenColor,
    f"\n{colorBlock} limeColor", globalHandler.limeColor,
    f"\n{colorBlock} blueColor", globalHandler.blueColor,
    f"\n{colorBlock} lightBlueColor", globalHandler.lightBlueColor,
    f"\n{colorBlock} darkBlueColor", globalHandler.darkBlueColor,
    f"\n{colorBlock} cyanColor", globalHandler.cyanColor,
    f"\n{colorBlock} whiteColor", globalHandler.whiteColor,
    f"\n{colorBlock} greyColor", globalHandler.greyColor,
    f"\n{colorBlock} lightGreyColor", globalHandler.lightGreyColor,
    f"\n{colorBlock} blackColor", globalHandler.blackColor,
    f"\n{colorBlock} purpleColor", globalHandler.purpleColor)
    add_output("1", globalHandler.redColor, "2", globalHandler.lightRedColor, "3", globalHandler.darkRedColor, "4", globalHandler.pinkColor, "5", globalHandler.orangeColor, "6", globalHandler.lightOrangeColor, 
               "7", globalHandler.darkOrangeColor, "8", globalHandler.yellowColor, "9", globalHandler.lightYellowColor, "10", globalHandler.darkYellowColor, "11", globalHandler.greenColor, 
               "12", globalHandler.lightGreenColor, "13", globalHandler.darkGreenColor, "14", globalHandler.limeColor, "15", globalHandler.blueColor, "16", globalHandler.lightBlueColor, 
               "17", globalHandler.darkBlueColor, "18", globalHandler.cyanColor, "19", globalHandler.whiteColor, "20", globalHandler.greyColor, "21", globalHandler.lightGreyColor, "22", globalHandler.blackColor, "23", globalHandler.purpleColor)


def clear_output():
    output_text.config(state=tk.NORMAL)
    output_text.delete(1.0, tk.END)
    output_text.config(state=tk.DISABLED)


def quit_app():
    rootWindow.destroy()


def add_output(*params):
    textVarPos = 0
    colorVarPos = 1
    for i in range(0, len(params), 2):
        text = params[textVarPos]
        color = params[colorVarPos]

        output_text.config(state=tk.NORMAL)
        output_text.insert(tk.END, text, color)
        output_text.tag_config(color, foreground=color)
        output_text.see(tk.END)
        output_text.config(state=tk.DISABLED)

        textVarPos = textVarPos + 2
        colorVarPos = colorVarPos + 2

    output_text.config(state=tk.NORMAL)
    output_text.insert(tk.END, "\n")
    output_text.see(tk.END)
    output_text.config(state=tk.DISABLED)


def on_enter(event):
    process_input()


def on_entry_focus_in(event):
    if entry.get() == placeholder_text:
        entry.delete(0, tk.END)
        entry.configure(show="")


def on_entry_focus_out(event):
    if entry.get() == "":
        entry.insert(0, placeholder_text)
        entry.configure(show="")
        
        
def navigate_history(event):
    if event.keysym == 'Up':
        if globalHandler.input_history and globalHandler.history_index > 0:
            globalHandler.history_index -= 1
            entry.delete(0, tk.END)
            entry.insert(0, globalHandler.input_history[globalHandler.history_index])
    elif event.keysym == 'Down':
        if globalHandler.input_history and globalHandler.history_index < len(globalHandler.input_history) - 1:
            globalHandler.history_index += 1
            entry.delete(0, tk.END)
            entry.insert(0, globalHandler.input_history[globalHandler.history_index])
        elif globalHandler.history_index == len(globalHandler.input_history) - 1:
            entry.delete(0, tk.END)
            globalHandler.history_index = len(globalHandler.input_history)


def toggle_fullscreen(event):
    globalHandler.fullscreen = not globalHandler.fullscreen
    rootWindow.attributes('-fullscreen', globalHandler.fullscreen)

#--------------------------------------------------------------------
os.system("")
globalHandler.init()

print(f"[Main][Info] Version: {globalHandler.ver}\n[Main][Info] Version name: {globalHandler.verName}")

IOHandler.load_config()

if globalHandler.accs_support:
    print("[Main][Info] Waiting for response")
    accWindow(selectable = True, top = False, icon = True)

IOHandler.load_save()
IOHandler.load_theme()

print("[Main][Info] \033[91mTo hide console window run Launcher.pyw\033[0m")

if globalHandler.autoSave:
    print("[Main][Info] autoSave is enabled... Skipping save console output")

update_prices()

name_generator()

available_commands = {
    "ver": "Display current version",
    "help": "Display available commands",
    "exit": "Close CommandMiner 2",
    "mine": "Mine ores",
    "sell": "Sell ores and get money",
    "upgrade pickaxe": "Upgrade pickaxe",
    "upgrade backpack": "Increase backpack size",
    "upgrade ore": "Upgrade your ore",
    "open <crate_tier>": "Open a desired crate",
    "clear": "Clear all text on the screen",
    "save": "Save your progress",
    "rebirth": "Exchange progress for tokens",
    "tokenshop": "Exchange tokens for skills",
    "stats": "See your statistics",
    "reset": "Resets your progress",
    "settings": "Configure CommandMiner 2",
    "crates": "See the amount of crates you have"
}

available_commands_dev = {
    "colortest": "Color test screen",
    "rlsave": "Reload save file",
    "rlconfig": "Reload config file",
    "globals": "Show all global items",
    "moddict": "Dump function_mod_dict"
}

function_dict = {
    'exit': 'quit_app()',
    'quit': 'quit_app()',
    'ver': 'add_output(f"CommandMiner 2 version: {globalHandler.ver}\\n{globalHandler.verName}", globalHandler.lightGreenColor)',
    'help dev': 'help_page("dev")',
    'help': 'help_page()',
    'mine': 'mine_ore()',
    'm': 'mine_ore()',
    'sell': 'sell_ore()',
    's': 'sell_ore()',
    'upgrade pickaxe': 'upgrade_pickaxe()',
    'u p': 'upgrade_pickaxe()',
    'up p': 'upgrade_pickaxe()',
    'upgrade backpack': 'upgrade_backpack()',
    'u b': 'upgrade_backpack()',
    'up b': 'upgrade_backpack()',
    'up bp': 'upgrade_backpack()',
    'u bp': 'upgrade_backpack()',
    'upgrade ore': 'upgrade_ore()',
    'up o': 'upgrade_ore()',
    'u o': 'upgrade_ore()',
    'up ore': 'upgrade_ore()',
    'o': 'add_output("[Error] ", globalHandler.lightRedColor, "Invalid syntax, use ", globalHandler.redColor, "o <crate_name>", globalHandler.lightYellowColor)',
    'open': 'add_output("[Error] ", globalHandler.lightRedColor, "Invalid syntax, use ", globalHandler.redColor, "open <crate_name>", globalHandler.lightYellowColor)',
    'open common': 'open_crate(crate_name="Common", crate_var_name="common_crate", reward_range=(10, 200), unlucky_threshold=150, reward_color=globalHandler.whiteColor)',
    'o common': 'open_crate(crate_name="Common", crate_var_name="common_crate", reward_range=(10, 200), unlucky_threshold=150, reward_color=globalHandler.whiteColor)',
    'o c': 'open_crate(crate_name="Common", crate_var_name="common_crate", reward_range=(10, 200), unlucky_threshold=150, reward_color=globalHandler.whiteColor)',
    'open c': 'open_crate(crate_name="Common", crate_var_name="common_crate", reward_range=(10, 200), unlucky_threshold=150, reward_color=globalHandler.whiteColor)',
    'open uncommon': 'open_crate(crate_name="Uncommon", crate_var_name="uncommon_crate", reward_range=(30, 400), unlucky_threshold=365, reward_color=globalHandler.lightGreenColor)',
    'o uncommon': 'open_crate(crate_name="Uncommon", crate_var_name="uncommon_crate", reward_range=(30, 400), unlucky_threshold=365, reward_color=globalHandler.lightGreenColor)',
    'o u': 'open_crate(crate_name="Uncommon", crate_var_name="uncommon_crate", reward_range=(30, 400), unlucky_threshold=365, reward_color=globalHandler.lightGreenColor)',
    'open u': 'open_crate(crate_name="Uncommon", crate_var_name="uncommon_crate", reward_range=(30, 400), unlucky_threshold=365, reward_color=globalHandler.lightGreenColor)',
    'open rare': 'open_crate(crate_name="Rare", crate_var_name="rare_crate", reward_range=(70, 625), unlucky_threshold=620, reward_color=globalHandler.lightBlueColor)',
    'o rare': 'open_crate(crate_name="Rare", crate_var_name="rare_crate", reward_range=(70, 625), unlucky_threshold=620, reward_color=globalHandler.lightBlueColor)',
    'o r': 'open_crate(crate_name="Rare", crate_var_name="rare_crate", reward_range=(70, 625), unlucky_threshold=620, reward_color=globalHandler.lightBlueColor)',
    'open r': 'open_crate(crate_name="Rare", crate_var_name="rare_crate", reward_range=(70, 625), unlucky_threshold=620, reward_color=globalHandler.lightBlueColor)',
    'open epic': 'open_crate(crate_name="Epic", crate_var_name="epic_crate", reward_range=(165, 925), unlucky_threshold=924, reward_color=globalHandler.purpleColor)',
    'o epic': 'open_crate(crate_name="Epic", crate_var_name="epic_crate", reward_range=(165, 925), unlucky_threshold=924, reward_color=globalHandler.purpleColor)',
    'o e': 'open_crate(crate_name="Epic", crate_var_name="epic_crate", reward_range=(165, 925), unlucky_threshold=924, reward_color=globalHandler.purpleColor)',
    'open e': 'open_crate(crate_name="Epic", crate_var_name="epic_crate", reward_range=(165, 925), unlucky_threshold=924, reward_color=globalHandler.purpleColor)',
    'open legendary': 'open_crate(crate_name="Legendary", crate_var_name="legendary_crate", reward_range=(230, 1300), unlucky_threshold=1999, reward_color=globalHandler.yellowColor)',
    'o legendary': 'open_crate(crate_name="Legendary", crate_var_name="legendary_crate", reward_range=(230, 1300), unlucky_threshold=1999, reward_color=globalHandler.yellowColor)',
    'o l': 'open_crate(crate_name="Legendary", crate_var_name="legendary_crate", reward_range=(230, 1300), unlucky_threshold=1999, reward_color=globalHandler.yellowColor)',
    'open l': 'open_crate(crate_name="Legendary", crate_var_name="legendary_crate", reward_range=(230, 1300), unlucky_threshold=1999, reward_color=globalHandler.yellowColor)',
    'open all': 'open_crate_all()',
    'o all': 'open_crate_all()',
    'o a': 'open_crate_all()',
    'open a': 'open_crate_all()',
    'tokenshop': 'token_shop()',
    'token shop': 'token_shop()',
    'tshop': 'token_shop()',
    'ts': 'token_shop()',
    'rebirth': 'rebirth()',
    'clear': 'clear_output()',
    'cls': 'clear_output()',
    'save': 'save_progress()',
    'stats': 'stats()',
    'update': 'add_output(f"Get the latest version at ", globalHandler.whiteColor, "https://fireroth.github.io/projects/cmdminer2", globalHandler.lightBlueColor)',
    'crates': 'allCrates()',
    'reset': 'reset_progress()',
    'buy': 'add_output("[Error] ", globalHandler.lightRedColor, "Invalid syntax, use ", globalHandler.redColor, "buy <product_name>", globalHandler.lightYellowColor)',
    'buy autosell': 'buy_autosell()',
    'buy rebreward': 'buy_rebreward()',
    'buy minmined': 'buy_minmined()',
    'buy autocrates': 'buy_autocrates()',
    'buy doublemine': 'buy_doublemine()',
    'colortest':'colorOutputTest()',
    'rlconfig':'IOHandler.load_config()',
    'rlsave':'IOHandler.load_save()',
    'globals':'add_output(globals(), globalHandler.lightYellowColor)',
    'moddict':'add_output(globalHandler.function_mod_dict, globalHandler.lightYellowColor)',
    'settings':'settingsWindow()',
    'help mods':'add_output("Available mod commands:\\n", globalHandler.blueColor, globalHandler.mod_commands, globalHandler.lightYellowColor)',
    'mods':'add_output("Loaded mods:\\n", globalHandler.lightRedColor, globalHandler.mod_list, globalHandler.whiteColor)',
    'set':'settingsWindow()',
    'accounts':'accWindow(selectable = False, top = True, icon = False)',
    'accs':'accWindow(selectable = False, top = True, icon = False)'
}

rootWindow = tk.Tk()
rootWindow.title("CommandMiner 2")
rootWindow.geometry("900x520")
rootWindow.minsize(width=600, height=400)
rootWindow.configure(background=globalHandler.globalBg)

icon = tk.PhotoImage(file="./images/icon.png")
rootWindow.iconphoto(True, icon)

backpack_icon = tk.PhotoImage(file="images/bag.png")
pickaxe_icon = tk.PhotoImage(file="images/wooden_pickaxe.png")
ore_icon = tk.PhotoImage(file="images/coal.png")
money_icon = tk.PhotoImage(file="images/money.png")
tokens_icon = tk.PhotoImage(file="images/tokens.png")

top_frame = tk.Frame(rootWindow)
top_frame.pack(padx=20, pady=10)

money_label = tk.Label(top_frame, text=f"Money: {globalHandler.money}", image=money_icon, compound='left', bg=f"{globalHandler.globalBg}", fg=f"{globalHandler.titleFg}", font=("", 10))
money_label.pack(side="left", padx=0)

separator_label1 = tk.Label(top_frame, text=" | ", bg=f"{globalHandler.globalBg}", fg=f"{globalHandler.titleFg}", font=("", 10))
separator_label1.pack(side="left", padx=0)

tokens_label = tk.Label(top_frame, text=f"Tokens: {globalHandler.tokens}", image=tokens_icon, compound='left', bg=f"{globalHandler.globalBg}", fg=f"{globalHandler.titleFg}", font=("", 10))
tokens_label.pack(side="left", padx=0)

separator_label2 = tk.Label(top_frame, text=" | ", bg=f"{globalHandler.globalBg}", fg=f"{globalHandler.titleFg}", font=("", 10))
separator_label2.pack(side="left", padx=0)

backpack_label = tk.Label(top_frame, text=f"Backpack: {globalHandler.ore_amount}/{globalHandler.backpack_capacity}", image=backpack_icon, compound='left', bg=f"{globalHandler.globalBg}", fg=f"{globalHandler.titleFg}", font=("", 10))
backpack_label.pack(side="left", padx=0)

separator_label3 = tk.Label(top_frame, text=" | ", bg=f"{globalHandler.globalBg}", fg=f"{globalHandler.titleFg}", font=("", 10))
separator_label3.pack(side="left", padx=0)

pickaxe_label = tk.Label(top_frame, text=f"Pickaxe level: {globalHandler.pickaxe_level}", image=pickaxe_icon, compound='left', bg=f"{globalHandler.globalBg}", fg=f"{globalHandler.titleFg}", font=("", 10))
pickaxe_label.pack(side="left", padx=0)

separator_label4 = tk.Label(top_frame, text=" | ", bg=f"{globalHandler.globalBg}", fg=f"{globalHandler.titleFg}", font=("", 10))
separator_label4.pack(side="left", padx=0)

ore_label = tk.Label(top_frame, text=f"Ore: {globalHandler.ore_name}", image=ore_icon, compound='left', bg=f"{globalHandler.globalBg}", fg=f"{globalHandler.titleFg}", font=("", 10))
ore_label.pack(side="left", padx=0)

output_text = scrolledtext.ScrolledText(rootWindow, wrap=tk.WORD, state=tk.DISABLED, background=f'{globalHandler.consoleBg}', fg=globalHandler.whiteColor, height=15, relief="flat", font=("", globalHandler.output_font_size))
output_text.pack(expand=True, fill="both")

placeholder_text = "Enter command here..."
entry = tk.Entry(rootWindow, background=f'{globalHandler.entryBg}', fg=f'{globalHandler.titleFg}', insertbackground=globalHandler.whiteColor, relief="flat", font=("", 17))
entry.insert(0, placeholder_text)

entry.bind("<FocusIn>", on_entry_focus_in)
entry.bind("<FocusOut>", on_entry_focus_out)
rootWindow.bind("<F11>", toggle_fullscreen)

if globalHandler.auto_focus:
    entry.focus()
entry.pack(pady=(0,7), fill='x')

button_frame = tk.Frame(rootWindow, background=f'{globalHandler.globalBg}')
button_frame.pack()

style = ttk.Style(button_frame)
style.configure("Main.TButton", foreground=globalHandler.buttonFg)

# Force the background color to work
style.layout("Main.TButton", [
    ("Button.border", {"sticky": "nswe", "children": [
        ("Button.background", {"sticky": "nswe", "children": [
            ("Button.label", {"sticky": "nswe"})
        ]})
    ]})
])

style.configure("Main.TButton", background=globalHandler.buttonBg)
style.map("Main.TButton", background=[("active", globalHandler.greyColor)])

quit_button = ttk.Button(button_frame, text="Quit", command=quit_app, style="Main.TButton")
quit_button.pack(side=tk.LEFT, padx=5, pady=(0,7))

process_button = ttk.Button(button_frame, text="Process", command=process_input, style="Main.TButton")
process_button.pack(side=tk.LEFT, padx=5, pady=(0,7))

help_button = ttk.Button(button_frame, text="Help", command=help_page, style="Main.TButton")
help_button.pack(side=tk.LEFT, padx=5, pady=(0,7))

settings_button = ttk.Button(button_frame, text="Settings", command=settingsWindow, style="Main.TButton")
settings_button.pack(side=tk.LEFT, padx=5, pady=(0,7))

if globalHandler.accs_support:
    accounts_button = ttk.Button(button_frame, text="Accounts", command=lambda: accWindow(selectable = False, top = True, icon = False), style="Main.TButton")
    accounts_button.pack(side=tk.LEFT, padx=5, pady=(0,7))

entry.bind("<Return>", on_enter)
entry.bind('<Up>', navigate_history)
entry.bind('<Down>', navigate_history)

add_output("CommandMiner 2 ", globalHandler.lightBlueColor, f"{globalHandler.verName}", globalHandler.blueColor)
if globalHandler.saveLoaded:
    if globalHandler.autoSave:
        add_output("Save file loaded successfully", globalHandler.lightGreenColor, " | ", globalHandler.whiteColor, "AutoSaving is enabled", globalHandler.lightGreenColor)
    else:
        add_output("Save file loaded successfully", globalHandler.lightGreenColor)
else:
    if globalHandler.autoSave:
        add_output("Save file was not loaded", globalHandler.redColor, " | ", globalHandler.whiteColor, "AutoSaving is enabled", globalHandler.lightGreenColor)
    else:
        add_output("Save file was not loaded", globalHandler.redColor)

if globalHandler.accs_support:
    add_output("Logged as ", globalHandler.orangeColor, globalHandler.account, globalHandler.orangeColor)

if globalHandler.mod_support:
    load_mods()

update_top_label()

rootWindow.mainloop()


if not globalHandler.autoSave and globalHandler.exitWarn and messagebox.askyesno("Not so fast...", "Do you want to save your progress before exiting?"):
    print("[Main] Saving and exiting")
    save_progress("silent")
exit()
