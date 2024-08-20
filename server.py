import http.server
import socketserver
import urllib.parse as urlparse
import os

import sqlite3


PORT = 8000 

def init_db():
    conn = sqlite3.connect('./data/params.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS request_params (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            param1 TEXT,
            param2 TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_params(param1, param2):
    conn = sqlite3.connect('./data/params.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO request_params (param1, param2)
        VALUES (?,?)
    ''', (param1, param2))
    conn.commit()
    conn.close()


class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):

        if self.path == '/':
            self.path = '/index.html'
        
        if os.path.exists(self.path[1:]):
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

        parsed_path = urlparse.urlparse(self.path)
        query_params = urlparse.parse_qs(parsed_path.query)
        
        param1 = query_params.get('param1', [''])[0]
        param2 = query_params.get('param2', [''])[0]

        log_params(param1, param2)

        response = f"""
        <html>
        <head>
            <title>GET Request Handler</title>
        </head>
        <body>
            <h1>GET Request Received</h1>
            <p><strong>Param 1:</strong> {param1}</p>
            <p><strong>Param 2:</strong> {param2}</p>
            <a href="/">Go back</a>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes(str(response), "utf8"))

if __name__ == "__main__":
    init_db()
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()
