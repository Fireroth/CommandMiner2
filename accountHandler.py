import tkinter as tk
from tkinter import ttk, messagebox
import globalHandler
import os

def load_accounts():
    try:
        with open("./data/accounts.dat", "r") as file:
            loaded_accounts = [line.strip() for line in file.readlines() if line.strip()]
    except FileNotFoundError:
        loaded_accounts = []
    if "Main" not in loaded_accounts:
        loaded_accounts.insert(0, "Main")
    return loaded_accounts


def save_account(account):
    with open("./data/accounts.dat", "a") as file:
        file.write(account + "\n")


def remove_account():
    selected_account = remove_account_var.get()
    if selected_account and selected_account != "Main":
        accounts.remove(selected_account)
        with open("./data/accounts.dat", "w") as file:
            for account in accounts:
                file.write(account + "\n")
        dropdown['values'] = accounts
        remove_dropdown['values'] = [acc for acc in accounts if acc != "Main"]

        del_confirm = messagebox.askyesno("Remove save file?", "Do you also want to remove the save file ot this account?")
        if del_confirm == True:
            os.remove(f"./data/save_{selected_account}.dat") 
        messagebox.showinfo("Success", f"Account '{selected_account}' removed.")
    else:
        messagebox.showwarning("Error", "You cannot remove the default 'Main' account.")


def on_select():
    selected_account = account_var.get()
    if selected_account:
        globalHandler.account = selected_account
        print("[accountHandler] Selected account:", globalHandler.account)
        root_accounts.destroy()
    else:
        messagebox.showwarning("No Selection", "Please select an account.")


def add_account():
    new_account = new_account_var.get().strip()
    if new_account and new_account not in accounts:
        accounts.append(new_account)
        dropdown['values'] = accounts
        remove_dropdown['values'] = [acc for acc in accounts if acc != "Main"]
        new_account_var.set("")
        save_account(new_account)
        messagebox.showinfo("Success", f"Account '{new_account}' added.")
    elif not new_account:
        messagebox.showwarning("Input Error", "Please enter a valid account name.")
    else:
        messagebox.showwarning("Duplicate Entry", "This account already exists.")


def accWindow(selectable = False, top = False, icon = True):
    global accounts, new_account_var, remove_account_var, account_var, dropdown, remove_dropdown, root_accounts
    accounts = load_accounts()

    if top == False:
        root_accounts = tk.Tk()
    else:
        root_accounts = tk.Toplevel()

    if icon == True:
        icon = tk.PhotoImage(file="./images/icon.png")
        root_accounts.iconphoto(True, icon)

    root_accounts.title("Account Manager")
    root_accounts.geometry("300x150")

    notebook = ttk.Notebook(root_accounts)
    notebook.pack(expand=True, fill='both')

    frame1 = ttk.Frame(notebook)
    notebook.add(frame1, text="Select Account")

    label = tk.Label(frame1, text="Select an account:")
    label.pack(pady=10)

    account_var = tk.StringVar(value="Main")
    dropdown = ttk.Combobox(frame1, textvariable=account_var, values=accounts, state="readonly")
    dropdown.pack(pady=5)

    dropdown.set("Main")

    select_button = ttk.Button(frame1, text="Select", command=on_select)
    select_button.pack(pady=10)

    if selectable == False:
        notebook.hide(frame1)
    else: print("[accountHandler] Started in selectable mode")

    frame2 = ttk.Frame(notebook)
    notebook.add(frame2, text="Add Account")

    add_label = tk.Label(frame2, text="Enter new account:")
    add_label.pack(pady=10)

    new_account_var = tk.StringVar()
    new_account_entry = tk.Entry(frame2, textvariable=new_account_var)
    new_account_entry.pack(pady=5)

    add_button = ttk.Button(frame2, text="Add", command=add_account)
    add_button.pack(pady=10)

    frame3 = ttk.Frame(notebook)
    notebook.add(frame3, text="Remove Account")

    remove_label = tk.Label(frame3, text="Select an account to remove:")
    remove_label.pack(pady=10)

    remove_account_var = tk.StringVar()
    remove_dropdown = ttk.Combobox(frame3, textvariable=remove_account_var, values=[acc for acc in accounts if acc != "Main"], state="readonly")
    remove_dropdown.pack(pady=5)

    remove_button = ttk.Button(frame3, text="Remove", command=remove_account)
    remove_button.pack(pady=10)

    root_accounts.mainloop()



if __name__ == "__main__":
    accWindow(selectable = False)
else:
    print("[Import] accountHandler imported as module")
