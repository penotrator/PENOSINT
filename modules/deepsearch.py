import os

from modules.misc import clearCLI, Colors, headers
from modules.breachcheck import breachCheck
from modules.username import userSearch

def deepsearch(username):
    if username == "None":
        print("Please input username")
    while not username or username == "None":
        username = input("$ ").strip()
        if not username:
            print(f"\n{Colors['RED']}Empty – try again.{Colors['RESET']}\n")
        else:
            clearCLI()

    print1 = userSearch(username, "deep")
    #print("\n" + "─" * os.get_terminal_size().columns)
    #filtered = [
    #line for line in print1
    #    if "────────────────────────────────────────────────────────────" not in line
    #]

    #print()
    #print("\n".join(filtered))
    #print("\n", print1)