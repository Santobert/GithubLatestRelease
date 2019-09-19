from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import requests
from typing import Optional

OWNER = "home-assistant"
REPO = "home-assistant"
URL = f"https://api.github.com/repos/{OWNER}/{REPO}/releases"


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def get_latest_version(self) -> Optional[dict]:
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

    def do_GET(self):
        """Handle a get request."""
        latest_version = self.get_latest_version()
        if latest_version is None:
            self.send_error(500, "The requested repository could not be reached")
        else:
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(latest_version), "utf-8"))
            return

    def do_POST(self):
        """Handle a post request."""
        content_length = int(self.headers["Content-Length"])
        body = self.rfile.read(content_length)
        # do sth with that body

        latest_version = self.get_latest_version()
        if latest_version is None:
            self.send_error(500, "The requested repository could not be reached.")
        else:
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(latest_version), "utf-8"))

if __name__ == "__main__":
    server_address = ('', 80)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    httpd.serve_forever()
