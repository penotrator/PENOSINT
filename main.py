import os
import getpass
from inspect import signature
from colorama import init

from modules.misc import clearCLI, Colors, Exit, ascii_table
from modules import misc as settings

from modules import username
from modules import breachcheck
from modules import deepsearch
from modules import geoip
from modules import configure
from modules import phonenumber

init(autoreset=True)

page = 1

commands = {
    '1': ("username", "Scan for a username on over 700+ websites.", username.userSearch),
    '2': ("breach-check", "Check if a username/email has been breached.", breachcheck.breachCheck),
    '0': ("deep-search", "Uses all modules to build a profile on the username/email", deepsearch.deepsearch),
    '99': ("exit", "Quits the program.", Exit),
}

commands2 = {
    '1': ("geo-ip", "Information about IP given.", geoip.geoip),
    '2': ("phone-lookup", "Information about given phonenumber.", phonenumber.phonelookup),
    '99': ("exit", "Quits the program.", Exit),
}

PARAM_EXAMPLES = {
    'username': 'johndoe',
    'usernameslashemail': 'johndoe/johndoe@gmail.com',
    'email': 'johndoe@gmail.com',
    'ip': '127.0.0.1',
    'phonenumber': "+447901123456"
}

def get_example(p):
    if p in PARAM_EXAMPLES:
        return PARAM_EXAMPLES[p]
    return p.replace('slash', '/')

pages = {
    1: commands,
    2: commands2
}

def helpCommand():
    current_commands = pages.get(page, commands)

    headers = ["#", "Function", "Description", "Params"]
    data = []

    for number, (cmd, desc, func) in current_commands.items():
        params = ", ".join(
            p.replace("slash", "/")
            for p in signature(func).parameters
        )

        data.append([number, cmd, desc, params])

    print(ascii_table(headers, data))

def getBanner():
    config = settings.load()
    return f"""{Colors["DIM"]}8888888b.  8888888888 888b    888  .d88888b.   .d8888b. 8888888 888b    888 88888888888 
888   Y88b 888        8888b   888 d88P" "Y88b d88P  Y88b  888   8888b   888     888     
888    888 888        88888b  888 888     888 Y88b.       888   88888b  888     888   ┌───────────────────────────────┐
888   d88P 8888888    888Y88b 888 888     888  "Y888b.    888   888Y88b 888     888   {Colors['RESET']+Colors["YellowB"] + Colors["YELLOW"]}│{Colors["BLACK"]} https://github.com/penotrator {Colors["YELLOW"]}│{Colors["RESET"] + Colors["DIM"]}
8888888P"  888        888 Y88b888 888     888     "Y88b.  888   888 Y88b888     888   ├───────────────┬───────────────┤
888        888        888  Y88888 888     888       "888  888   888  Y88888     888   {Colors['RESET']+Colors["YellowB"] + Colors["YELLOW"]}│{Colors["BLACK"]} Version       {Colors["YELLOW"]}│{Colors["BLACK"]}           v{config['Version']}  {Colors["YELLOW"]}│{Colors["RESET"] + Colors["DIM"]}
888        888        888   Y8888 Y88b. .d88P Y88b  d88P  888   888   Y8888     888   └───────────────┴───────────────┘
888        8888888888 888    Y888  "Y88888P"   "Y8888P" 8888888 888    Y888     888   {Colors["RESET"]}[Page {page}/2]{Colors["RESET"]}"""

def get_current_user():
    try:
        return os.getlogin()
    except OSError:
        return os.environ.get("USER") or os.environ.get("USERNAME") or getpass.getuser() or "user"

try:
    os.system("Title PENOSINT")

    while True:
        current_commands = pages.get(page, commands)

        clearCLI()
        print(getBanner())
        helpCommand()
        print()

        raw = input(
            f'{Colors["RESET"]}┌── <{get_current_user()}@PENOSINT> ─ [~]\n└──╼ $ '
        ).strip()

        if not raw:
            continue

        command_parts = raw.split()
        command = command_parts[0]
        
        if command == "config":
            clearCLI()
            configure.configure()
            continue

        if command.startswith("page"):
            try:
                new_page = int(command_parts[1])

                if new_page in pages:
                    page = new_page
                else:
                    print(f'\n{Colors["RED"]}Page does not exist.{Colors["RESET"]}\n')
                    print("─" * os.get_terminal_size().columns + "\n")
                    settings.pause()

            except (IndexError, ValueError):
                print(f'\n{Colors["RED"]}Usage: page <number>{Colors["RESET"]}\n')
                print("─" * os.get_terminal_size().columns + "\n")
                settings.pause()

            continue

        if command.startswith("help"):
            try:
                commandNum = command_parts[1]

                if commandNum in current_commands:
                    cmd_name, desc, func = current_commands[commandNum]
                    params = " ".join(f"|{get_example(p)}|" for p in signature(func).parameters)
                    print(f'\n{Colors["YELLOW"]}{desc}{Colors["RESET"]}')
                    print(f'Usage: {Colors["DIM"]}"{commandNum} {params}"{Colors["RESET"]}\n')
                else:
                    print(f'\n{Colors["RED"]}Command not found.{Colors["RESET"]}\n')

                print("─" * os.get_terminal_size().columns + "\n")
                settings.pause()

            except (IndexError, ValueError):
                print(f'\n{Colors["RED"]}Usage: help <number>{Colors["RESET"]}\n')
                print("─" * os.get_terminal_size().columns + "\n")
                settings.pause()

            continue

        if command not in current_commands:
            print(f'\n{Colors["RED"]}Invalid command.{Colors["RESET"]}\n')
            print("─" * os.get_terminal_size().columns + "\n")
            settings.pause()
            continue

        params = []
        current = ""
        inside = False

        for part in command_parts[1:]:
            stripped = part.strip('|')

            if part.startswith('|') and part.endswith('|'):
                params.append(stripped)

            elif part.startswith('|'):
                inside = True
                current = stripped

            elif part.endswith('|'):
                inside = False
                params.append(f"{current} {stripped}")

            elif inside:
                current += f" {part}"

        clearCLI()

        func = current_commands[command][2]
        sig = signature(func).parameters

        try:
            if len(sig) >= len(params):
                func(*params, *['None'] * (len(sig) - len(params)))

            else:
                param_names = " ".join(sig)

                print(
                    f'{Colors["RED"]}Too many parameters! '
                    f'{Colors["YELLOW"]}"{command}"{Colors["RED"]} expects: '
                    f'{Colors["YELLOW"]}{param_names}{Colors["RESET"]}'
                )

        except KeyboardInterrupt:
            print(f'\n{Colors["YELLOW"]}Command cancelled.{Colors["RESET"]}')
            continue

        print("\n" + "─" * os.get_terminal_size().columns + "\n")
        settings.pause()

except KeyboardInterrupt:
    print()
    Exit()