import aiohttp
import asyncio
import re
import json
import os
import requests
from time import time
from tqdm.asyncio import tqdm as async_tqdm
import random, string

from modules.misc import clearCLI, Colors, headers
from modules import misc as settings
from modules.breachcheck import breachCheck

def access_json_property(data, path_config):
    try:
        value = data
        for key in path_config:
            value = value[key]
        return value
    except Exception:
        return False

def access_html_regex(data, pattern):
    try:
        match = re.search(pattern, data)
        if match:
            return match.group(1).replace("\n", "")
    except Exception:
        return False

def extract_metadata(metadata, response_text, response_json, site):
    extracted = []
    for params in metadata:
        meta_return = dict(params)
        prefix = params.get("prefix", "")

        if params["schema"] == "JSON":
            return_value = access_json_property(response_json, params["path"])
        elif params["schema"] == "HTML":
            return_value = access_html_regex(response_text, params["path"])
        else:
            continue

        if return_value is "" or return_value == None:
            continue

        if params["type"] == "String":
            if isinstance(return_value, str):
                return_value = return_value.replace("\n", "")
            meta_return["value"] = f"{prefix}{return_value}" if prefix else str(return_value)

        elif params["type"] == "Array" and isinstance(return_value, list):
            meta_return["value"] = [
                access_json_property(item, meta_return["item-path"])
                for item in return_value
            ]

        extracted.append(meta_return)
    return extracted

def load_sites():
    try:
        with open("sites.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        response = requests.get(
            "https://raw.githubusercontent.com/penotrator/PENOSINT/main/sites.json"
        )
        data = response.json()
    return data["sites"], data["sitesdata"]

async def check_site(session, site, username, metadata):
    uri = site["uri_check"].format(account=username)
    try:
        async with session.get(uri) as res:
            if res.status != site["e_code"]:
                return None

            raw = await res.content.read(102_400)
            text = raw.decode("utf-8", errors="ignore")

            if site["e_string"] not in text or site["m_string"] in text:
                return None

            response_json = None
            site_name = site["name"]
            if site_name in metadata:
                needs_json = any(
                    p["schema"] == "JSON" for p in metadata[site_name]
                )
                if needs_json:
                    try:
                        response_json = json.loads(text)
                    except Exception:
                        response_json = {}

            extracted = []
            if site_name in metadata:
                extracted = extract_metadata(
                    metadata[site_name], text, response_json, site
                )

            return site_name, uri, extracted, site.get("cat", "")

    except Exception:
        return None

async def _run_search(username, sites, metadata, timeoutnum):
    timeout = aiohttp.ClientTimeout(total=timeoutnum)
    connector = aiohttp.TCPConnector(
        limit=150,
        ttl_dns_cache=300,
        ssl=False,
        enable_cleanup_closed=True,
    )

    found = []

    async with aiohttp.ClientSession(
        headers=headers,
        connector=connector,
        timeout=timeout,
    ) as session:
        tasks = [
            asyncio.create_task(check_site(session, site, username, metadata))
            for site in sites
        ]

        pbar = async_tqdm(
            asyncio.as_completed(tasks),
            total=len(tasks),
            desc=f"Scanning \033[1m{username}\033[0m",
        )

        for coro in pbar:
            try:
                result = await coro
                if result:
                    found.append(result)
            except Exception:
                pass

    return found

def generate_html(username, found_sites, fname, output):
    from html import escape

    sections = []

    for site_name, uri, meta_list, site_cat in found_sites:
        meta_html = ""

        for meta in meta_list:
            val = meta.get("value", "")
            if val:
                meta_html += f"""
                <div class="meta">
                    <span class="meta-name">{escape(meta['name'])}</span>
                    <span class="meta-value">{escape(str(val))}</span>
                </div>
                """

        sections.append(f"""
        <div class="card">
            <div class="card-header">
                <a href="{uri}" target="_blank">{escape(site_name)}</a>
            </div>
            <div class="card-body">
                {meta_html if meta_html else '<div class="no-meta">No metadata</div>'}
            </div>
        </div>
        """)

    aggregated = {
        "Email": [],
        "Location": [],
        "Country": [],
        "IP": [],
        "Name": [],
        "Computer Name": [],
        "Operating System": [],
        "Date Compromised": [],
    }

    IMPORTANT_FIELDS = set(aggregated.keys())

    for site_name, uri, meta_list, site_cat in found_sites:
        for meta in meta_list:
            val = meta.get("value")
            if val in ("None", "[]", None, [], "null"):
                continue

            if meta["name"] in IMPORTANT_FIELDS:
                entry = f"{val} ({site_name})"
                if entry not in aggregated[meta["name"]]:
                    aggregated[meta["name"]].append(entry)

    summary_html = ""
    summary_printed = False

    for field, values in aggregated.items():
        if values:
            summary_printed = True
            summary_html += f"""
            <div class="summary-item">
                <span class="summary-label">{field}:</span>
                <span class="summary-value">{' | '.join(map(str, values))}</span>
            </div>
            """

    if summary_printed:
        summary_html = f"""
        <div class="summary">
            <h2>Key Intelligence Summary</h2>
            {summary_html}
        </div>
        """

    divider_html = '<div class="divider"></div>' if summary_printed else ''
    divider2_html = '<div class="divider"></div>'

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{username}</title>

<style>
body {{
    margin: 0;
    background: #0b0f17;
    font-family: Arial, sans-serif;
    color: #e6edf3;
}}

.container {{
    max-width: 900px;
    margin: auto;
    padding: 30px;
}}

h1 {{
    text-align: center;
    margin-bottom: 30px;
    color: #58a6ff;
}}

.card {{
    background: #161b22;
    border-radius: 10px;
    margin-bottom: 20px;
    padding: 15px 20px;
    box-shadow: 0 0 10px rgba(0,0,0,0.4);
    transition: 0.2s;
}}

.card:hover {{
    transform: translateY(-2px);
}}

.card-header a {{
    color: #58a6ff;
    text-decoration: none;
    font-weight: bold;
    font-size: 16px;
}}

.card-header a:hover {{
    text-decoration: underline;
}}

.meta {{
    margin-top: 6px;
    font-size: 14px;
}}

.meta-name {{
    color: #8b949e;
}}

.meta-value {{
    margin-left: 8px;
    color: #e6edf3;
}}

.no-meta {{
    color: #6e7681;
    font-style: italic;
}}

.summary {{
    background: #11161d;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 10px;
    box-shadow: 0 0 10px rgba(0,0,0,0.4);
}}

.summary h2 {{
    margin-top: 0;
    color: #58a6ff;
    font-size: 18px;
}}

.summary-item {{
    margin-top: 8px;
    font-size: 14px;
}}

.summary-label {{
    color: #8b949e;
}}

.summary-value {{
    margin-left: 6px;
    color: #e6edf3;
}}

.divider {{
    height: 3px;
    background: #ffffff;
    margin: 30px 0;
    border-radius: 2px;
    opacity: 0.9;
}}

.footer {{
    margin-top: 40px;
    text-align: center;
    font-size: 12px;
    color: #6e7681;
}}

.footer a {{
    color: #58a6ff;
    text-decoration: none;
}}

.footer a:hover {{
    text-decoration: underline;
}}
</style>
</head>

<body>

<div class="container">
    {divider2_html}
    {summary_html}
    {divider_html}

    {"".join(sections)}
    {divider2_html}

    <div class="footer">
        <a href="https://github.com/penotrator/PENOSINT" target="_blank">
            https://github.com/penotrator/PENOSINT
        </a>
    </div>
</div>

</body>
</html>
"""

    os.makedirs(output, exist_ok=True)
    with open(os.path.join(output, fname), "w", encoding="utf-8") as f:
        f.write(html)
    print(f'[{Colors['GREEN']}+{Colors['RESET']}] Saved {output}{fname}')

def userSearch(username, deep):
    config = settings.load()
    HudsonRockDataFound = False
    EmailsFound = 0
    Emails = []
    TopLogins = []
    blocked_nsfw = 0

    if username == "None":
        print("Please input username")
    while not username or username == "None":
        username = input("$ ").strip()
        if not username:
            print(f"\n{Colors['RED']}Empty – try again.{Colors['RESET']}\n")
        else:
            clearCLI()

    if deep == "None":
        timeoutnum = config['timeout']
    else:
        timeoutnum = config['timeout'] + 5

    sites, metadata = load_sites()
    start_time = time()

    try:
        found_sites = asyncio.run(_run_search(username, sites, metadata, timeoutnum))
    except KeyboardInterrupt:
        return

    all_results = [(username, found_sites)]

    if deep != "None" and found_sites:
        searched = {username.lower()}
        username_fields = {"displayName", "Twitter username", "Name History"}

        pending = []
        for site_name, uri_check, meta_list, site_cat in found_sites:
            for meta in meta_list:
                val = meta.get('value', 'N/A')
                if val in ("None", "[]", None, [], 'N/A'):
                    continue
                if meta['name'] in username_fields and val.lower() not in searched:
                    searched.add(val.lower())
                    pending.append(val)

        if pending:
            clearCLI()
            print(
                f"{Colors['DIM']}[→] Deep mode (Finished {username}): found {len(pending)} linked "
                f"username(s), searching...{Colors['RESET']}"
            )
            for linked_user in pending:
                try:
                    linked_found = asyncio.run(_run_search(linked_user, sites, metadata, timeoutnum))
                except KeyboardInterrupt:
                    print(f"\n{Colors['RED']}Deep search interrupted.{Colors['RESET']}")
                    break
                all_results.append((linked_user, linked_found))

    elapsed = time() - start_time

    lines = []
    any_found = any(fs for _, fs in all_results)

    aggregated = {
        "Email": [],
        "Location": [],
        "Country": [],
        "IP": [],
        "Full name": [],
        "Name": [],
        "Computer Name": [],
        "Operating System": [],
        "Date Compromised": [],
    }
    IMPORTANT_FIELDS = set(aggregated.keys())
    all_possible_usernames = []
    username_fields = {"displayName", "Twitter username", "Name History"}
    all_searched_usernames = {u.lower() for u, _ in all_results}

    if any_found:
        print("\n" + "─" * os.get_terminal_size().columns)

        for current_user, current_sites in all_results:
            if not current_sites:
                continue
            user_blocked_nsfw = 0

            print(
                f"\n\033[32m[✓]{Colors['RESET']} \033[1m{current_user}\033[0m — "
                f"{len(current_sites)} profile(s) found"
            )
            lines.append(f"\n{current_user} ({len(current_sites)} sites)")
            lines.append("─" * 60)

            for site_name, uri_check, meta_list, site_cat in current_sites:
                if site_name == "HudsonRock":
                    HudsonRockDataFound = True
                if site_cat == "xx NSFW xx" and config["exclude_NSFW_results"]:
                    blocked_nsfw += 1
                    user_blocked_nsfw += 1
                    continue
                print(
                    f"  {Colors['GreenB']}{Colors['BLACK']}+{Colors['RESET']} "
                    f"\033[1m{site_name}\033[0m - {Colors['DIM']}{uri_check}{Colors['RESET']}"
                )
                lines.append(f"[+] {site_name} - {uri_check}")
                for meta in meta_list:
                    val = meta.get('value', 'N/A')
                    if val in ("None", "[]", None, []):
                        continue
                    if meta['name'] == "Email" and val not in ("null", "", "N/A", " ", None):
                        EmailsFound += 1
                        Emails.append(f'{val} ─ ({site_name}) ({current_user})')
                    if meta['name'] == "Top Logins" and isinstance(val, list):
                        TopLogins = val
                        email_logins = [v for v in val if isinstance(v, str) and v.endswith(".com")]
                        for e in email_logins:
                            if e not in Emails:
                                EmailsFound += 1
                                Emails.append(f'{e} ─ ({site_name}) ({current_user})')
                        continue
                    print(
                        f"  {Colors['DIM']}└─ {meta['name']}: "
                        f"{val}{Colors['RESET']}"
                    )
                    lines.append(f"    └─ {meta['name']}: {val}")
                    if meta['name'] in IMPORTANT_FIELDS:
                        entry = f"{val} ({current_user})"
                        if entry not in aggregated[meta['name']]:
                            aggregated[meta['name']].append(entry)
                    if meta['name'] in username_fields:
                        if val.lower() not in all_searched_usernames and val not in ("None", "[]", None, [], 'N/A'):
                            entry = (val, current_user, site_name, meta['name'])
                            if entry not in all_possible_usernames:
                                all_possible_usernames.append(entry)

            if user_blocked_nsfw:
                print(f"  {Colors['DIM']}[{user_blocked_nsfw} NSFW result(s) hidden]{Colors['RESET']}")

            if config["auto_save"]:
                ran = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                fname = f"{current_user}-{ran}.html"
                generate_html(current_user, current_sites, fname, config["output_dir"])

        print("\n" + "─" * os.get_terminal_size().columns)
        print(f"\n\033[1m[~] Key Intelligence Summary\033[0m")
        lines.append("\n" + "─" * 60)
        lines.append("\nKey Intelligence Summary")

        summary_printed = False
        for field, values in aggregated.items():
            if values:
                summary_printed = True
                label_color = {
                    "Email":            Colors['RED'],
                    "Location":         Colors['RED'],
                    "Country":          Colors['RED'],
                    "IP":               Colors['RED'],
                    "Name":             Colors['YELLOW'],
                    "Full name":        Colors['RED'],
                    "Computer Name":    Colors['RED'],
                    "Operating System": Colors['DIM'],
                    "Date Compromised": Colors['DIM'],
                }.get(field, Colors['RESET'])
                print(
                    f"  {label_color}{field}:{Colors['RESET']} "
                    + f", ".join(values)
                )
                lines.append(f"  {field}: {', '.join(str(v) for v in values)}")

        if all_possible_usernames:
            summary_printed = True
            print(f"\n  {Colors['RESET']}Possible Linked Username(s):")
            lines.append("\n  Possible Linked Username(s):")
            for val, found_on_user, site_name, field_name in all_possible_usernames:
                print(f"    {Colors['DIM']}└─ {val} ─ ({field_name}) ({found_on_user}/{site_name}){Colors['RESET']}")
                lines.append(f"    └─ {val} ─ {field_name} ({found_on_user}/{site_name})")

        if Emails:
            summary_printed = True
            unique_emails = list(dict.fromkeys(Emails))
            label = "Email" if len(unique_emails) == 1 else "Emails"
            print(f"\n  Possible {label} Found:")
            lines.append(f"\n  {label} Found:")
            for email in unique_emails:
                print(f"    {Colors['DIM']}└─ {email}{Colors['RESET']}")
                lines.append(f"    └─ {email}")

        if not summary_printed:
            print(f"  {Colors['DIM']}No key metadata found.{Colors['RESET']}")
            lines.append("  No key metadata found.")

        print("\n" + "─" * os.get_terminal_size().columns)
        print(f"\n[{Colors['YELLOW']}*{Colors['RESET']}] Took {elapsed:.2f}s.")
        lines.append(f"\nTook {elapsed:.2f}s.")

        if HudsonRockDataFound:
            print(
                f"{Colors['RESET']}\nCheck {username} for a breach? (y/n) "
                f"- ({Colors['RED']}HudsonRock data found{Colors['RESET']})"
            )
            if input("$ ").strip().lower() == "y":
                print("\n" + "─" * os.get_terminal_size().columns)
                breachCheck(username)

    else:
        print(
            f"\n{Colors['RED']}\033[1mNo profiles found for "
            f"{username}.{Colors['RESET']}\033[0m"
        )

    return lines