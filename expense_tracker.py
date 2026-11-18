"""
Personal Expense Tracker (CLI)
==============================

A small command-line app that lets you:
    1. Add an expense (amount, category, date)
    2. View all expenses
    3. See total spend per category
    4. Save/load everything to a data.json file

How to run:
    python expense_tracker.py

How the code is organized (top to bottom):
    - Settings          : constants like the data file name
    - Storage           : functions that load/save the JSON file
    - Input helpers     : functions that ask the user for a valid value
    - Core features     : add, view, and summarize expenses
    - Menu / main loop  : the part that ties everything together

Each function does ONE job. That makes the code easier to read, test,
and change later (this idea is called "separation of concerns").
"""

import json                      # Built-in module for reading/writing JSON files
from datetime import date, datetime  # Built-in tools for working with dates
from pathlib import Path         # Modern, cross-platform way to handle file paths


# ---------------------------------------------------------------------------
# SETTINGS
# ---------------------------------------------------------------------------

# Path(__file__) is the location of THIS script. .with_name() swaps the file
# name, so data.json always lives next to the script, no matter which folder
# you run the program from.
DATA_FILE = Path(__file__).with_name("data.json")

# The date format we expect the user to type, e.g. 2026-11-18.
# %Y = 4-digit year, %m = 2-digit month, %d = 2-digit day.
DATE_FORMAT = "%Y-%m-%d"


# ---------------------------------------------------------------------------
# STORAGE: loading and saving data
# ---------------------------------------------------------------------------
# We store expenses as a list of dictionaries, like this:
#   [
#       {"amount": 12.5, "category": "Food", "date": "2026-11-18"},
#       {"amount": 40.0, "category": "Transport", "date": "2026-11-19"}
#   ]
# JSON handles lists, dictionaries, numbers, and strings natively, which is
# why it is a great fit for this kind of data.

def load_expenses():
    """Read expenses from data.json and return them as a list.

    If the file doesn't exist yet (first run) or is damaged, we return an
    empty list instead of crashing, so the app always starts cleanly.
    """
    if not DATA_FILE.exists():
        return []  # First run: nothing saved yet.

    try:
        # "with" automatically closes the file for us when we're done.
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)  # Convert JSON text -> Python list
    except (json.JSONDecodeError, OSError):
        # JSONDecodeError: the file contains invalid JSON.
        # OSError: the file couldn't be read (permissions, etc.).
        print("Warning: could not read data.json. Starting with an empty list.")
        return []


def save_expenses(expenses):
    """Write the list of expenses to data.json.

    indent=2 makes the file human-readable (nicely spaced out).
    """
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(expenses, file, indent=2)  # Python list -> JSON text
    except OSError as error:
        print(f"Error: could not save data: {error}")


# ---------------------------------------------------------------------------
# INPUT HELPERS: keep asking until the user gives a valid answer
# ---------------------------------------------------------------------------
# User input is unpredictable (typos, letters instead of numbers, etc.).
# These helpers loop until they get something valid, so the rest of the
# program can trust the values it receives.

def ask_for_amount():
    """Ask for a positive number and return it as a float."""
    while True:  # Repeat until we return a valid value
        text = input("Amount: ").strip()
        try:
            amount = float(text)  # Raises ValueError if text isn't a number
        except ValueError:
            print("  Please enter a number, e.g. 12.50")
            continue  # Jump back to the top of the loop

        if amount <= 0:
            print("  Amount must be greater than zero.")
            continue

        return round(amount, 2)  # Keep 2 decimal places (cents)


def ask_for_category():
    """Ask for a non-empty category name and return it in Title Case."""
    while True:
        category = input("Category (e.g. Food, Transport, Rent): ").strip()
        if category:  # An empty string is "falsy", so this checks it's not empty
            # .title() makes "food" and "FOOD" both become "Food",
            # so the same category is never split into two by capitalization.
            return category.title()
        print("  Category cannot be empty.")


def ask_for_date():
    """Ask for a date (YYYY-MM-DD). Pressing Enter uses today's date."""
    while True:
        text = input("Date (YYYY-MM-DD, press Enter for today): ").strip()

        if text == "":
            return date.today().strftime(DATE_FORMAT)  # Date -> text

        try:
            # strptime parses text into a datetime; it raises ValueError
            # if the text doesn't match the format (or is an impossible
            # date such as 2026-02-30).
            parsed = datetime.strptime(text, DATE_FORMAT)
            return parsed.strftime(DATE_FORMAT)  # Store it in a clean format
        except ValueError:
            print("  Invalid date. Use the format YYYY-MM-DD, e.g. 2026-11-18")


# ---------------------------------------------------------------------------
# CORE FEATURES
# ---------------------------------------------------------------------------

def add_expense(expenses):
    """Collect details from the user and add a new expense to the list."""
    print("\n--- Add Expense ---")
    expense = {
        "amount": ask_for_amount(),
        "category": ask_for_category(),
        "date": ask_for_date(),
    }
    expenses.append(expense)  # Modifies the list in place
    save_expenses(expenses)   # Save right away so nothing is lost if we crash
    print(f"Added: ${expense['amount']:.2f} for {expense['category']} "
          f"on {expense['date']}")


def view_expenses(expenses):
    """Print every expense in a neat table, oldest date first."""
    print("\n--- All Expenses ---")

    if not expenses:
        print("No expenses recorded yet.")
        return

    # sorted() returns a NEW sorted list and leaves the original untouched.
    # "key" tells Python what to sort by; ISO dates (YYYY-MM-DD) sort
    # correctly as plain text, which is a nice benefit of that format.
    ordered = sorted(expenses, key=lambda e: e["date"])

    # In an f-string, "<12" means "left-align in 12 characters" and
    # ">10" means "right-align in 10 characters". This lines up the columns.
    print(f"{'Date':<12} {'Category':<15} {'Amount':>10}")
    print("-" * 39)
    for expense in ordered:
        print(f"{expense['date']:<12} {expense['category']:<15} "
              f"{expense['amount']:>10.2f}")

    print("-" * 39)
    print(f"{'Total':<28} {calculate_total(expenses):>10.2f}")


def calculate_total(expenses):
    """Return the sum of all expense amounts.

    The inner expression is a "generator expression": it walks through each
    expense and pulls out its amount, and sum() adds them up.
    """
    return sum(expense["amount"] for expense in expenses)


def calculate_totals_by_category(expenses):
    """Return a dictionary like {"Food": 52.5, "Rent": 800.0}."""
    totals = {}
    for expense in expenses:
        category = expense["category"]
        # .get(key, 0) returns the current total, or 0 if we haven't seen
        # this category yet. This avoids a KeyError on the first occurrence.
        totals[category] = totals.get(category, 0) + expense["amount"]
    return totals


def view_totals_by_category(expenses):
    """Print the total spend for each category, biggest first."""
    print("\n--- Total Spend by Category ---")

    if not expenses:
        print("No expenses recorded yet.")
        return

    totals = calculate_totals_by_category(expenses)

    # totals.items() gives (category, amount) pairs. We sort by amount
    # (item[1]) from highest to lowest using reverse=True.
    for category, amount in sorted(totals.items(), key=lambda item: item[1],
                                   reverse=True):
        print(f"{category:<15} {amount:>10.2f}")

    print("-" * 26)
    print(f"{'Total':<15} {calculate_total(expenses):>10.2f}")


# ---------------------------------------------------------------------------
# MENU AND MAIN LOOP
# ---------------------------------------------------------------------------

def show_menu():
    """Print the list of choices."""
    print("\n===== Personal Expense Tracker =====")
    print("1. Add expense")
    print("2. View all expenses")
    print("3. View total spend by category")
    print("4. Save and exit")


def main():
    """Program entry point: load data, then loop on the menu until exit."""
    expenses = load_expenses()
    print(f"Loaded {len(expenses)} expense(s) from {DATA_FILE.name}.")

    while True:
        show_menu()
        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            add_expense(expenses)
        elif choice == "2":
            view_expenses(expenses)
        elif choice == "3":
            view_totals_by_category(expenses)
        elif choice == "4":
            save_expenses(expenses)
            print("Data saved. Goodbye!")
            break  # Leave the while loop, which ends the program
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")


# This guard means main() only runs when you execute this file directly
# (python expense_tracker.py). If another file imports this one, for
# example to test its functions, main() will NOT run automatically.
if __name__ == "__main__":
    main()
