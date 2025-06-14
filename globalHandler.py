def init():
    global ver, verName, ore_amount, money, tokens, pickaxe_level, pickaxe_name, backpack_capacity, backpack_name
    global backpack_level, saveLoaded, ore_multiplier, ore_name, common_crate, uncommon_crate, rare_crate, epic_crate
    global legendary_crate, autosell, rebirth_token_reward, rebirth_amount, minimum_mined, auto_crate_open, double_mine, account

    global colorsName, sepChar, output_font_size, auto_focus, autoSave, exitWarn, mod_support, accs_support

    global globalBg, consoleBg, buttonBg, entryBg, titleFg, buttonFg
    global redColor, lightRedColor, darkRedColor, pinkColor, orangeColor, lightOrangeColor, darkOrangeColor, yellowColor
    global lightYellowColor, darkYellowColor, greenColor, lightGreenColor, darkGreenColor, limeColor, blueColor, lightBlueColor
    global darkBlueColor, cyanColor, whiteColor, greyColor, blackColor, purpleColor, lightGreyColor

    global mod_list, mod_commands, history_index, fullscreen, input_history, function_mod_dict
    
    #Main
    account = "Main"
    saveLoaded = False
    ver = "2.7.1"
    verName = "Random fixes mini-update"
    ore_amount = 0
    money = 0
    tokens = 0
    pickaxe_level = 1
    pickaxe_name = "Wooden"
    backpack_capacity = 50
    backpack_level = 1
    backpack_name = "Wooden"
    ore_multiplier = 1
    ore_name = "Coal"
    common_crate = 0
    uncommon_crate = 0
    rare_crate = 0
    epic_crate = 0
    legendary_crate = 0
    autosell = 0
    rebirth_token_reward = 0
    rebirth_amount = 0
    minimum_mined = 0
    auto_crate_open = 0
    double_mine = 0

    #Config
    colorsName = "Dark"
    sepChar = "No spacing"
    output_font_size = 12
    auto_focus = False
    autoSave = True
    exitWarn = True
    mod_support = False
    accs_support = False

    #Theme UI
    globalBg = "#FFF"
    consoleBg = "#FFF"
    buttonBg = "#FFF"
    entryBg = "#FFF"
    titleFg = "#000"
    buttonFg = "#000"

    #Theme colors
    redColor = "#000"
    lightRedColor = "#000"
    darkRedColor = "#000"
    pinkColor = "#000"
    orangeColor = "#000"
    lightOrangeColor = "#000"
    darkOrangeColor = "#000"
    yellowColor = "#000"
    lightYellowColor = "#000"
    darkYellowColor = "#000"
    greenColor = "#000"
    lightGreenColor = "#000"
    darkGreenColor = "#000"
    limeColor = "#000"
    blueColor = "#000"
    lightBlueColor = "#000"
    darkBlueColor = "#000"
    cyanColor = "#000"
    whiteColor = "#000"
    greyColor = "#000"
    blackColor = "#000"
    purpleColor = "#000"
    lightGreyColor = "#000"

    #Misc
    mod_commands = ""
    mod_list = ""
    history_index = -1
    fullscreen = False
    input_history = [""]
    function_mod_dict = {}

    print("[globalHandler] Successfully loaded globals")


if __name__ == "__main__":
    print("Run Launcher.pyw or main.py")
    _ = input("Press Enter to exit...")

else:
    print("[Import] globalHandler imported as module")
