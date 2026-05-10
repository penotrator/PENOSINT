import phonenumbers
from phonenumbers import carrier, geocoder, timezone

from modules.misc import clearCLI, Colors

def phonelookup(phonenumber='None'):
    if phonenumber == "None":
        print("Please input phone number (e.g. +447901123456)")
    while not phonenumber or phonenumber == "None":
        phonenumber = input("$ ").strip()

        if not phonenumber:
            print(f"\n{Colors['RED']}Empty – try again.{Colors['RESET']}\n")
        else:
            clearCLI()

    try:
        parsed = phonenumbers.parse(phonenumber)

        if not phonenumbers.is_valid_number(parsed):
            print(f"\n{Colors['RED']}Invalid phone number.{Colors['RESET']}")
            return

        isp          = carrier.name_for_number(parsed, 'en') or "Unknown"
        location     = geocoder.description_for_number(parsed, 'en') or "Unknown"
        time_zones   = timezone.time_zones_for_number(parsed)
        number_type  = phonenumbers.number_type(parsed)
        intl_format  = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        natl_format  = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
        e164_format  = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        country_code = parsed.country_code
        region       = phonenumbers.region_code_for_number(parsed)

        type_map = {
            0: "Fixed line",
            1: "Mobile",
            2: "Fixed or Mobile",
            3: "Toll free",
            4: "Premium rate",
            6: "VOIP",
            7: "Personal number",
            99: "Unknown",
        }
        number_type_str = type_map.get(number_type, "Unknown")

        fields = [
            ("Number (Intl)",  intl_format),
            ("Number (Natl)",  natl_format),
            ("E164",           e164_format),
            ("Country Code",   f"+{country_code}"),
            ("Region",         region),
            ("Location",       location),
            ("Carrier/ISP",    isp),
            ("Type",           number_type_str),
            ("Timezone(s)",    ", ".join(time_zones) if time_zones else "Unknown"),
        ]

        print()
        for k, v in fields:
            if v:
                print(f"  {k:<15}: {v}")

    except phonenumbers.phonenumberutil.NumberParseException as e:
        print(f"\n{Colors['RED']}Could not parse number: {e}{Colors['RESET']}")
    except Exception as e:
        print(f"\n{Colors['RED']}Error: {e}{Colors['RESET']}")