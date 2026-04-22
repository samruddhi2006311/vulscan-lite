import requests

def check_headers(url):
    # Make sure url starts with https://
    if not url.startswith("http"):
        url = "https://" + url

    # These are the 3 security headers we check
    headers_to_check = [
        "Content-Security-Policy",
        "X-Frame-Options",
        "Strict-Transport-Security"
    ]

    score = 0
    passed = []
    failed = []

    try:
        # Send a GET request to the website
        response = requests.get(url, timeout=10)
        response_headers = response.headers

        # Check each security header
        for header in headers_to_check:
            if header in response_headers:
                score += 10
                passed.append(header)
            else:
                score -= 10
                failed.append(header)

        return {
            "url": url,
            "score": score,
            "passed": passed,
            "failed": failed,
            "error": None
        }

    except requests.exceptions.RequestException as e:
        return {
            "url": url,
            "score": 0,
            "passed": [],
            "failed": headers_to_check,
            "error": str(e)
        }