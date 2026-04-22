import ssl
import socket
from datetime import datetime

def check_ssl(url):
    # Remove https:// or http:// to get just the domain name
    domain = url.replace("https://", "").replace("http://", "").split("/")[0]

    try:
        # Step 1 — Create a secure connection to the website
        context = ssl.create_default_context()
        conn = context.wrap_socket(
            socket.socket(socket.AF_INET),
            server_hostname=domain
        )

        # Step 2 — Connect to port 443 (this is the standard HTTPS port)
        conn.connect((domain, 443))

        # Step 3 — Get the certificate information
        cert = conn.getpeercert()
        conn.close()

        # Step 4 — Read the expiry date from the certificate
        expire_date_str = cert['notAfter']
        expire_date = datetime.strptime(expire_date_str, "%b %d %H:%M:%S %Y %Z")

        # Step 5 — Check how many days until it expires
        today = datetime.utcnow()
        days_left = (expire_date - today).days

        # Step 6 — Get the cipher (encryption strength)
        cipher = conn.cipher() if not conn._closed else "Unknown"

        # Step 7 — Decide if certificate is valid
        is_valid = days_left > 0

        return {
            "domain": domain,
            "is_valid": is_valid,
            "days_left": days_left,
            "expires_on": expire_date.strftime("%d %B %Y"),
            "error": None
        }

    except ssl.SSLCertVerificationError:
        return {
            "domain": domain,
            "is_valid": False,
            "days_left": 0,
            "expires_on": None,
            "error": "Certificate is invalid or untrusted"
        }

    except Exception as e:
        return {
            "domain": domain,
            "is_valid": False,
            "days_left": 0,
            "expires_on": None,
            "error": str(e)
        }