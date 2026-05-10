import requests
import os

from modules.misc import clearCLI, Colors
from modules import misc as settings

def breachCheck(usernameslashemail: str) -> None:
    config = settings.load()
    api_key = config["BreachDirectory"]

    while not api_key:
        print(f"{Colors['RED']}You don’t have a BreachDirectory API key.{Colors['RESET']}")
        print(f"Get one at {Colors['YELLOW']}https://rapidapi.com/rohan-patra/api/breachdirectory{Colors['RESET']}")
        api_key = input("$ ").strip()
        if api_key:
            config["BreachDirectory"] = api_key
            settings.save(config)
            clearCLI()
        else:
            print(f"{Colors['RED']}Empty key – try again.{Colors['RESET']}")
    if usernameslashemail == "None":
        print("Please input username/email:")
    while not usernameslashemail or usernameslashemail == "None":
        usernameslashemail = input("$ ").strip()

        if not usernameslashemail:
            print(f"\n{Colors['RED']}Empty – try again.{Colors['RESET']}\n")
    clearCLI()

    use_dehash = input(f"{Colors['RESET']}Dehash lookup? (y/n) - (Uses more requests){Colors['RESET']}\n$ ").strip().lower()
    use_dehash = use_dehash == "y"

    bd_url = "https://breachdirectory.p.rapidapi.com/"
    headers = {
        "x-rapidapi-host": "breachdirectory.p.rapidapi.com",
        "x-rapidapi-key": api_key,
    }

    try:
        auto_j = requests.get(
            bd_url,
            headers=headers,
            params={"func": "auto", "term": usernameslashemail},
            timeout=15
        ).json()
    except Exception as e:
        print(f"\n{Colors['RED']}Could not reach BreachDirectory ({e}){Colors['RESET']}")
        return

    if isinstance(auto_j, dict) and "message" in auto_j:
        print(f"\n{Colors['RED']}API error:{Colors['YELLOW']} {auto_j['message']}{Colors['RESET']}{Colors['DIM']} (You can change your API in config.){Colors['RESET']}")
        return

    hits = auto_j.get("result", [])
    if not hits:
        print(f"\n{Colors['RED']}No breaches found for {usernameslashemail}{Colors['RESET']}")
        return

    raw_entries: list[tuple[str, list[str] | str]] = []
    lines = []

    print(f"\n{Colors['GREEN']}[+] Found entries - {len(hits)}{Colors['RESET']}")
    lines.append(f"[+] Found entries - {len(hits)}\n")

    passwords = 0
    for hit in hits:
        sha1_hash = hit.get("sha1")
        hash_val = hit.get("hash")
        passcensored = hit.get("password")
        sources = hit.get("sources") or hit.get("source") or "?"

        if not sha1_hash:
            continue
        if passcensored:
            passwords += 1

        if isinstance(sources, list):
            src_str = ", ".join(sources)
        else:
            src_str = str(sources)

        print(f'  {Colors["GreenB"]}{Colors["BLACK"]}+{Colors["RESET"]} {src_str}')
        print(f'  └─ SHA1: {Colors["DIM"]}{sha1_hash}{Colors["RESET"]}')
        print(f'  └─ HASH: {Colors["DIM"]}{hash_val}{Colors["RESET"]}')
        print(f'  └─ PASS: {Colors["DIM"]}{passcensored}{Colors["RESET"]}')

        lines.append(f"+ {src_str}")
        lines.append(f"  └─ SHA1: {sha1_hash}")
        lines.append(f"  └─ HASH: {hash_val}")
        lines.append(f"  └─ PASS: {passcensored}")

        password = None
        if use_dehash:
            try:
                de_j = requests.get(
                    bd_url,
                    headers=headers,
                    params={"func": "dehash", "term": hash_val},
                    timeout=20,
                ).json()
            except Exception:
                de_j = None
            if isinstance(de_j, dict):
                password = de_j.get("found")
        if password:
            raw_entries.append((password, src_str))

    if raw_entries:
        lines.append("")
        print(f"\n{Colors['GREEN']}[+] {len(raw_entries)}/{passwords} Found for {usernameslashemail}{Colors['RESET']}")
        lines.append(f"[+] Clear passwords")
        for pwd, src in raw_entries:
            lines.append(f"  + {src}")
            lines.append(f"  └─ {pwd}")
            print(f'  {Colors["GreenB"]}{Colors["BLACK"]}+{Colors["RESET"]} \033[1m{src}\033[0m{Colors["RESET"]}\n  └─ {Colors["DIM"]}{pwd}{Colors["RESET"]}')
    else:
        print(f"\n{Colors['RED']}No clear passwords were retrieved{Colors['RESET']}")

    print("\nSave to .txt? (y/n)")
    if input("$ ").strip().lower() == "y":
        fname = os.path.join("..", f"{usernameslashemail}-search.txt")
        with open(fname, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        print(f"\n[{Colors['YELLOW']}*{Colors['RESET']}] Saved: {fname}")