import os
import getpass

from modules.misc import clearCLI, Colors, ascii_table
from modules import misc as settings

config_types = {
    "auto_save": bool,
    "exclude_NSFW_results": bool,
    "output_dir": str,
    "BreachDirectory": str,
    "timeout": int,
    "Version": int
}

def parse_value(key: str, value: str):
    expected = config_types.get(key)
    if expected == bool:
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
        return None
    return value

def parse_params(command_parts):
    params = []
    current = ""
    inside = False

    for part in command_parts:
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

    return params

def helpCommand():
    config = settings.load()
    if config:
        config_headers = ["#", "Setting/API", "Value"]
        config_data = [
            [i + 1, key, value]
            for i, (key, value) in enumerate(config.items())
            if key != "Version"
        ]
        print(ascii_table(config_headers, config_data))

def getBanner():
    config = settings.load()
    return f"""{Colors["RESET"]}8888888b.  8888888888 888b    888  .d88888b.   .d8888b. 8888888 888b    888 88888888888 
888   Y88b 888        8888b   888 d88P" "Y88b d88P  Y88b  888   8888b   888     888     
888    888 888        88888b  888 888     888 Y88b.       888   88888b  888     888   ┌───────────────────────────────┐
888   d88P 8888888    888Y88b 888 888     888  "Y888b.    888   888Y88b 888     888   {Colors["YellowB"] + Colors["YELLOW"]}│{Colors["BLACK"]} https://github.com/penotrator {Colors["YELLOW"]}│{Colors["ResetB"] + Colors["RESET"]}
8888888P"  888        888 Y88b888 888     888     "Y88b.  888   888 Y88b888     888   ├───────────────┬───────────────┤
888        888        888  Y88888 888     888       "888  888   888  Y88888     888   {Colors["YellowB"] + Colors["YELLOW"]}│{Colors["BLACK"]} Version       {Colors["YELLOW"]}│{Colors["BLACK"]}           {config['Version']}  {Colors["YELLOW"]}│{Colors["ResetB"] + Colors["RESET"]}
888        888        888   Y8888 Y88b. .d88P Y88b  d88P  888   888   Y8888     888   └───────────────┴───────────────┘
888        8888888888 888    Y888  "Y88888P"   "Y8888P" 8888888 888    Y888     888   {Colors["DIM"]}CTRL+C to go back{Colors["RESET"]}"""

def get_current_user():
    try:
        return os.getlogin()
    except OSError:
        return os.environ.get("USER") or os.environ.get("USERNAME") or getpass.getuser() or "user"

def configure():
    try:
        os.system("Title PENOSINT")

        while True:
            clearCLI()
            print(getBanner())
            helpCommand()
            print()

            raw = input(
                f'{Colors["RESET"]}┌── <{get_current_user()}@PENOSINT> ─ [~]\n└──╼ $ '
            ).strip()

            if not raw:
                print(f'\n{Colors["RED"]}Invalid command. (eg: "1 |value|"){Colors["RESET"]}\n')
                print("─" * os.get_terminal_size().columns + "\n")
                settings.pause()
                continue

            command_parts = raw.split()
            command = command_parts[0]
            params = parse_params(command_parts[1:])

            config = settings.load()
            config_keys = list(config.keys())

            if command == "reset":
                config['auto_save'] = True
                config['exclude_NSFW_results'] = True
                config['timeout'] = 5
                config['output_dir'] = "results/"
                config['BreachDirectory'] = ""
                config['Version'] = 2
                settings.save(config)
                continue

            if command.isdigit():
                index = int(command) - 1

                if not (0 <= index < len(config_keys)):
                    continue

                config_key = config_keys[index]
                expected_type = config_types.get(config_key)

                if expected_type == bool and not params:
                    config[config_key] = not config[config_key]
                    settings.save(config)
                    continue

                if not params:
                    print(f'{Colors['RED']}\nNo value provided. (eg: "1 |value|")\n{Colors['RESET']}')
                    print("─" * os.get_terminal_size().columns + "\n")
                    settings.pause()
                    continue

                parsed = parse_value(config_key, params[0])

                if parsed is None:
                    print(f'{Colors['RED']}\n"{config_key}" expects a {expected_type.__name__}.{Colors['RESET']}\n')
                    print("─" * os.get_terminal_size().columns + "\n")
                    settings.pause()
                    continue

                config[config_key] = parsed
                settings.save(config)

            else:
                print(f'{Colors['RED']}\nInvalid command. (eg: "1 |value|"){Colors['RESET']}\n')
                print("─" * os.get_terminal_size().columns + "\n")
                settings.pause()

            #print("─" * os.get_terminal_size().columns + "\n")
            #os.system("pause")

    except KeyboardInterrupt:
        print()
        return