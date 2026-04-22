import requests
from bs4 import BeautifulSoup

def check_cms(url):
    # Make sure url starts with https://
    if not url.startswith("http"):
        url = "https://" + url

    cms_name = None
    cms_version = None
    warnings = []

    try:
        response = requests.get(url, timeout=10)
        html = response.text
        headers = response.headers

        # --- Method 1: Check meta generator tag in HTML ---
        # Example: <meta name="generator" content="WordPress 6.1">
        soup = BeautifulSoup(html, "html.parser")
        meta_generator = soup.find("meta", attrs={"name": "generator"})

        if meta_generator:
            content = meta_generator.get("content", "")

            if "wordpress" in content.lower():
                cms_name = "WordPress"
                # Try to extract version number
                parts = content.split(" ")
                if len(parts) > 1:
                    cms_version = parts[1]

            elif "drupal" in content.lower():
                cms_name = "Drupal"
                parts = content.split(" ")
                if len(parts) > 1:
                    cms_version = parts[1]

            elif "joomla" in content.lower():
                cms_name = "Joomla"
                parts = content.split(" ")
                if len(parts) > 1:
                    cms_version = parts[1]

        # --- Method 2: Check X-Powered-By header ---
        # Example: X-Powered-By: PHP/7.4
        powered_by = headers.get("X-Powered-By", "")
        if powered_by:
            warnings.append(f"X-Powered-By header exposed: {powered_by}")

        # --- Method 3: Check WordPress specific paths ---
        if "/wp-content/" in html or "/wp-includes/" in html:
            cms_name = "WordPress"
            warnings.append("WordPress detected via page content")

        # Build result
        if cms_name:
            warnings.append(f"{cms_name} detected - keep it updated to avoid known vulnerabilities")

        return {
            "url": url,
            "cms_name": cms_name,
            "cms_version": cms_version,
            "warnings": warnings,
            "error": None
        }

    except requests.exceptions.RequestException as e:
        return {
            "url": url,
            "cms_name": None,
            "cms_version": None,
            "warnings": [],
            "error": str(e)
        }