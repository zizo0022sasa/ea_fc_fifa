#!/usr/bin/env python3
"""
Simple web server for testing interface
"""
import http.server
import socketserver
import os
import sys

PORT = 8080

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()
    
    def do_GET(self):
        if self.path == '/':
            self.path = '/test_interface.html'
        return super().do_GET()

os.chdir('/home/user/webapp/ea_fc_fifa')

with socketserver.TCPServer(("0.0.0.0", PORT), MyHTTPRequestHandler) as httpd:
    print(f"🌐 Server running at http://0.0.0.0:{PORT}/")
    print(f"📂 Serving files from: {os.getcwd()}")
    print("Press Ctrl+C to stop...")
    sys.stdout.flush()
    httpd.serve_forever()