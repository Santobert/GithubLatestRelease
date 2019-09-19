from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import requests

OWNER = "home-assistant"
REPO = "home-assistant"


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            r = requests.get(
                "https://api.github.com/repos/{}/{}/releases".format(OWNER, REPO)
            )
            r.raise_for_status()
        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
            self.send_error(500, "The requested repository could not be reached.")
            return

        releases = json.loads(r.content)
        for release in releases:
            if release["prerelease"] is True:
                continue

            result = {}
            result["release-notes"] = release["body"]
            result["version"] = release["name"]

            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(result), "utf-8"))
            return


httpd = HTTPServer(("localhost", 8080), SimpleHTTPRequestHandler)
httpd.serve_forever()
