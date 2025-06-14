import os
from typing import Literal

import dotenv
import segno

SecurityType = Literal["WPA", "WEP"]

dotenv.load_dotenv()


def wifi_qr_data(
    ssid: str,
    security: SecurityType | None,
    password: str,
    admin_password: str | None,
) -> str:
    return ";".join(
        [
            f"WIFI:S:{ssid}",
            f"T:{security or ''}",
            f"P:{password}",
            f"{admin_password or ''}",
            "",
        ]
    )


def main():
    ssid = os.environ["WIFI_SSID"]
    password = os.environ["WIFI_PASSWORD"]
    admin_password = os.environ["WIFI_ADMIN_PASSWORD"]
    security: SecurityType = "WPA"

    qr_data = wifi_qr_data(ssid, security, password, admin_password)
    qr_code = segno.make_qr(qr_data)
    qr_code.save("home-wifi-qr.png", scale=20)


if __name__ == "__main__":
    main()
