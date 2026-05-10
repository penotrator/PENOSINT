import requests
import socket

from modules.misc import clearCLI, Colors, headers

def geoip(ip='None'):
    if ip == "None":
        print("Please input IP")
    while not ip or ip == "None":
        ip = input("$ ").strip()

        if not ip:
            print(f"\n{Colors['RED']}Empty – try again.{Colors['RESET']}\n")
        else:
            clearCLI()
    try:
        d = requests.get(f"http://ip-api.com/json/{ip}?fields=66846719", timeout=6).json()
        if d.get("status") == "success":
            fields = [
                ("IP",         d.get("query")),
                ("Country",       f"{d.get('country')} ({d.get('countryCode')})"),
                ("Region",     d.get("regionName")),
                ("City",      d.get("city")),
                ("Code Postal",d.get("zip")),
                ("Lat/Lon",    f"{d.get('lat')}, {d.get('lon')}"),
                ("ISP",        d.get("isp")),
                ("Org",        d.get("org")),
                ("AS",         d.get("as")),
                ("Timezone",   d.get("timezone")),
                ("Mobile",     d.get("mobile")),
                ("Proxy/VPN",  d.get("proxy")),
                ("Hosting",  d.get("hosting")),
                ("Google Maps", f"https://maps.google.com/?q={d.get('lat')},{d.get('lon')}")
            ]
            print()
            for k, v in fields:
                if v:
                    print(f"  {k:<15}: {v}")
            try:
                rev = socket.gethostbyaddr(d.get("query", ""))[0]
                print(f"  {'Reverse DNS':<15}: {rev}")
            except:
                pass
        else:
            print("API refused.")
    except Exception as e:
        print(f"Error: {e}")