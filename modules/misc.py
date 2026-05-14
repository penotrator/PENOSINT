import os
import json
from colorama import Fore, Back, Style

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "en-US;q=0.9,en;q=0.8",
    "accept-encoding": "gzip, deflate",
    "user-Agent": "Mozilla/5.0 (Windows NT 10.0;Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
}

Colors = {
    "RED": Fore.RED,
    "GREEN": Fore.GREEN,
    "RESET": Style.RESET_ALL,
    "YELLOW": Fore.YELLOW,
    "BLACK": Fore.BLACK,

    "GreenB": Back.GREEN,
    "YellowB": Back.YELLOW,
    "ResetB": Back.RESET,
    "DIM": Style.DIM
}

def ascii_table(headers, data):
    max_lengths = [len(header) for header in headers]
    for row in data:
        for i, value in enumerate(row):
            max_lengths[i] = max(max_lengths[i], len(str(value)))
    
    table = ''
    
    header_row = '┌'
    for i, header in enumerate(headers):
        header_row += '─' * (max_lengths[i] + 2) + '┬' if i < len(headers) - 1 else '─' * (max_lengths[i] + 2) + '┐'
    table += header_row + '\n'
    
    header_row = '│'
    for i, header in enumerate(headers):
        header_row += f' {header.ljust(max_lengths[i])} │'
    table += header_row + '\n'
    
    horizontal_line = '├'
    for i, length in enumerate(max_lengths):
        horizontal_line += '─' * (length + 2) + '┼' if i < len(max_lengths) - 1 else '─' * (length + 2) + '┤'
    table += horizontal_line + '\n'

    for i, row in enumerate(data):
        if i % 2 == 0:
            data_row = f'{Fore.YELLOW}│{Fore.BLACK}'
        else:
            data_row = '│'

        for j, value in enumerate(row):
            cell_value = str(value).ljust(max_lengths[j])
            
            if i % 2 == 0:
                data_row += f' {cell_value} {Fore.YELLOW}│{Fore.BLACK}'
            else:
                data_row += f' {cell_value} │'

        if i % 2 == 0:
            table += Colors["BLACK"] + Colors["YellowB"] + data_row + Colors["RESET"] + '\n'
        else:
            table += data_row + '\n'

    bottom_line = '└'
    for i, length in enumerate(max_lengths):
        bottom_line += '─' * (length + 2) + '┴' if i < len(max_lengths) - 1 else '─' * (length + 2) + '┘'
    table += bottom_line
    
    return "\n" + table

def clearCLI():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    if os.name == 'nt':
        os.system('pause')
    else:
        input('Press Enter to continue...')

def Exit():
    quit()

CONFIG_FILE = "config.json"

def load():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)