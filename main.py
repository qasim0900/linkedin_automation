import logging
from tabulate import tabulate
from Linkedin import linkedin_main

# ---------------------------------------
# :: Main Function
# ---------------------------------------

"""
The function manages user selection, 
sets up the browser and database, and runs the chosen LinkedIn automation task with proper error handling and cleanup.
"""


def main():
    try:
        options = [
            ["1", "LinkedIn"],
            ["2", "Instragram"],
        ]
        choice = print("\nSelect an option (1-2): ")
        print(tabulate(options, headers=[
              "ID", "Action"], tablefmt="fancy_grid"))
        choice = int(input("choice: "))
        actions = {
            1: linkedin_main.main,
            2: None,
        }
        actions.get(choice, lambda: logging.warning(
            "Invalid choice. Please select 1-4."))()
    except Exception as e:
        logging.exception(f"Startup error: {e}")


if __name__ == "__main__":
    main()






