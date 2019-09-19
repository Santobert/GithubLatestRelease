from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import requests

OWNER = "home-assistant"
REPO = "home-assistant"


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def get_latest_version(self):
        try:
            r = requests.get(
                "https://api.github.com/repos/{}/{}/releases".format(OWNER, REPO)
            )
            r.raise_for_status()
        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
            return None

        releases = json.loads(r.content)
        for release in releases:
            if release["prerelease"] is True:
                continue

            result = {}
            result["release-notes"] = release["body"]
            result["version"] = release["name"]
            return result

    def do_GET(self):
        latest_version = self.get_latest_version()
        if latest_version is None:
            self.send_error(500, "The requested repository could not be reached.")
        else:
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(latest_version), "utf-8"))
            return

    def do_POST(self):
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


httpd = HTTPServer(("localhost", 8080), SimpleHTTPRequestHandler)
httpd.serve_forever()
