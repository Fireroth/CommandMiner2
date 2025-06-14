import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import globalHandler
import IOHandler
import json


def saveConfig():
    globalHandler.colorsName = theme_var.get()
    globalHandler.sepChar = separator_var.get()

    try:
        font_size = int(font_size_var.get())
        if font_size > 30:
            font_size = 30
        elif font_size < 8:
            font_size = 8
        globalHandler.output_font_size = font_size
    except ValueError:
        messagebox.showerror("Cannot save...", "Output Font Size only accepts numbers from 8 to 30")
        return

    globalHandler.auto_focus = auto_focus_var.get()
    globalHandler.autoSave = auto_save_var.get()
    globalHandler.exitWarn = exit_warning_var.get()
    globalHandler.mod_support = mod_support_var.get()
    globalHandler.accs_support = accs_support_var.get()

    IOHandler.save_config()
    root_settings.destroy()



def toggle_exit_warning():
    if auto_save_var.get() == 0:
        exit_warning_checkbox.config(state="normal")
    else:
        exit_warning_checkbox.config(state="disabled")


def settingsWindow():
    global theme_var, separator_var, font_size_var, auto_focus_var, auto_save_var, root_settings, exitWarn, mod_support, accs_support
    global colorsName, sepChar, output_font_size, auto_focus, autoSave, exit_warning_checkbox, exit_warning_var, mod_support_var, accs_support_var

    #default fallback values
    colorsName = "Dark"
    sepChar = "No spacing"
    output_font_size = 12
    auto_focus = False
    autoSave = True
    exitWarn = True
    mod_support = False
    accs_support = False

    try:
        with open("./data/config.json", "r") as file:
            config = json.load(file)

            colorsName = config.get("colorsName", "")
            sepChar = config.get("sepChar", "|")
            output_font_size = config.get("output_font_size", "12")
            auto_focus = config.get("auto_focus", "True")
            autoSave = config.get("autoSave", "False")
            exitWarn = config.get("exitWarn", "True")
            mod_support = config.get("mod_support", "False")
            accs_support = config.get("accs_support", "False")

    except FileNotFoundError:
        print("The 'config.json' file was not found.")
    except json.JSONDecodeError:
        print("Error decoding JSON from 'config.json'.")
    
    if __name__ == "__main__":
        root_settings = tk.Tk()
        icon = tk.PhotoImage(file="./images/icon.png")
        root_settings.iconphoto(True, icon)
    else:
        root_settings = tk.Toplevel()

    root_settings.title("Settings")
    root_settings.geometry("300x420")
    root_settings.minsize(width=220, height=300)

    notebook = ttk.Notebook(root_settings)
    notebook.pack(fill="both", expand=True, pady=(5, 0), padx=5)

    general_tab = ttk.Frame(notebook)
    notebook.add(general_tab, text="General")

    theme_frame = ttk.LabelFrame(general_tab, text="Theme")
    theme_frame.pack(fill="x", padx=10, pady=5)
    theme_var = tk.StringVar(theme_frame, value=colorsName)
    theme_menu = ttk.Combobox(theme_frame, textvariable=theme_var, values=["Dark", "Light", "Pastel", "Custom"], state="readonly")
    theme_menu.pack(fill="x", padx=10, pady=5)

    separator_frame = ttk.LabelFrame(general_tab, text="Command Output Separator")
    separator_frame.pack(fill="x", padx=10, pady=5)
    separator_var = tk.StringVar(value=sepChar)
    separator_menu = ttk.Combobox(separator_frame, textvariable=separator_var, values=["No spacing", "Empty line", "----------"], state="readonly")
    separator_menu.pack(fill="x", padx=10, pady=5)

    font_size_frame = ttk.LabelFrame(general_tab, text="Output Font Size")
    font_size_frame.pack(fill="x", padx=10, pady=5)
    font_size_var = tk.IntVar(value=output_font_size)
    font_size_spinbox = ttk.Spinbox(font_size_frame, from_=8, to=30, textvariable=font_size_var)
    font_size_spinbox.pack(fill="x", padx=10, pady=5)

    behavior_tab = ttk.Frame(notebook)
    notebook.add(behavior_tab, text="Behavior")

    focus_frame = ttk.LabelFrame(behavior_tab, text="Auto Focus to Input Field")
    focus_frame.pack(fill="x", padx=10, pady=5)
    auto_focus_var = tk.BooleanVar(value=auto_focus)
    focus_checkbox = ttk.Checkbutton(focus_frame, text="Enable", variable=auto_focus_var)
    focus_checkbox.pack(fill="x", padx=10, pady=5)

    autoSave_frame = ttk.LabelFrame(behavior_tab, text="AutoSave")
    autoSave_frame.pack(fill="x", padx=10, pady=5)
    auto_save_var = tk.BooleanVar(value=autoSave)
    autoSave_checkbox = ttk.Checkbutton(autoSave_frame, text="Enable", variable=auto_save_var, command=toggle_exit_warning)
    autoSave_checkbox.pack(fill="x", padx=10, pady=5)

    exit_warning_var = tk.BooleanVar(value=exitWarn)
    exit_warning_checkbox = ttk.Checkbutton(autoSave_frame, text="Show exit warning", variable=exit_warning_var)
    exit_warning_checkbox.pack(fill="x", padx=10, pady=5)

    advanced_tab = ttk.Frame(notebook)
    notebook.add(advanced_tab, text="Additional features")

    mods_frame = ttk.LabelFrame(advanced_tab, text="Mod Support")
    mods_frame.pack(fill="x", padx=10, pady=5)
    mod_support_var = tk.BooleanVar(value=mod_support)
    mod_support_checkbox = ttk.Checkbutton(mods_frame, text="Enable", variable=mod_support_var)
    mod_support_checkbox.pack(fill="x", padx=10, pady=5)

    accs_frame = ttk.LabelFrame(advanced_tab, text="Accounts Support")
    accs_frame.pack(fill="x", padx=10, pady=5)
    accs_support_var = tk.BooleanVar(value=accs_support)
    accs_support_checkbox = ttk.Checkbutton(accs_frame, text="Enable", variable=accs_support_var)
    accs_support_checkbox.pack(fill="x", padx=10, pady=5)

    warn_label = ttk.Label(root_settings, text="Any changes apply after CM2 restarts", foreground="red")
    warn_label.pack(fill="x", padx=10, pady=5)

    button_frame = tk.Frame(root_settings)
    button_frame.pack(fill="x", padx=10, pady=10)

    save_button = ttk.Button(button_frame, text="Save", command=saveConfig)
    save_button.pack(side="left", padx=5)

    cancel_button = ttk.Button(button_frame, text="Cancel", command=root_settings.destroy)
    cancel_button.pack(side="right", padx=5)

    toggle_exit_warning()
    root_settings.mainloop()

#--------------------------------------------------------------------

if __name__ == "__main__":
    settingsWindow()
else:
    print("[Import] settings imported as module")
