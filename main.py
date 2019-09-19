from flask import abort, Flask, request, Response
import json
import logging
import requests
from typing import Optional

OWNER = "home-assistant"
REPO = "home-assistant"
URL = f"https://api.github.com/repos/{OWNER}/{REPO}/releases"

app = Flask(__name__)


def get_latest_version() -> Optional[dict]:
    """Return the latest release that's not a prerelease."""

    # Request the github api for all releases
    try:
        r = requests.get(URL)
        r.raise_for_status()
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
        # Invalid or no response
        return None

    # Find the latest release thats not a prerelease
    try:
        releases = json.loads(r.content)
    except ValueError:
        # Invalid JSON
        return None
    for release in releases:
        if release["prerelease"] is True:
            continue

        result = {}
        result["release-notes"] = release["body"]
        result["version"] = release["name"]
        return result


@app.route("/", methods=["GET", "POST"])
def do_GET():
    """Handle a request."""
    if request.method == "POST":
        body = request.get_json()
        user = request.remote_addr
        # do sth with that body
        logging.info("%s posted %s", user, body)

    latest_version = get_latest_version()
    if latest_version is None:
        abort(500)
    else:
        response = Response(json.dumps(latest_version))
        response.headers["Content-Type"] = "application/json"
        return response


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, filename="info.log")
    app.run(host="0.0.0.0", port=80)
