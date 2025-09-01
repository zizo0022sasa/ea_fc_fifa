#!/usr/bin/env python3
import http.server
import socketserver
import os

PORT = 8888
os.chdir('/home/user/webapp/ea_fc_fifa')

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/test.html'
        return super().do_GET()

with socketserver.TCPServer(("0.0.0.0", PORT), MyHandler) as httpd:
    print(f"🌐 Server at http://0.0.0.0:{PORT}/")
    httpd.serve_forever()