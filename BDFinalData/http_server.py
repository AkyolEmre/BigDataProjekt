#!/usr/bin/env python3
"""
Robust HTTP Server for Crypto Dashboard
Handles timeouts and connection errors gracefully
"""

import http.server
import socketserver
import os
import sys
import signal
import time
from functools import partial

class RobustHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler with better error handling"""
    
    def __init__(self, *args, **kwargs):
        # Set timeout for each request
        self.timeout = 30
        super().__init__(*args, directory='.', **kwargs)
    
    def log_message(self, format, *args):
        """Custom logging to reduce noise"""
        # Only log actual requests, not every connection
        if '200' in str(args) or '404' in str(args):
            sys.stdout.write("%s - [%s] %s\n" %
                           (self.address_string(),
                            self.log_date_time_string(),
                            format % args))
    
    def end_headers(self):
        """Add headers to prevent caching issues"""
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    
    def handle(self):
        """Handle requests with timeout protection"""
        try:
            super().handle()
        except (ConnectionResetError, BrokenPipeError, TimeoutError):
            # Silently ignore connection errors
            pass
        except Exception as e:
            if 'WinError 10054' not in str(e):  # Ignore Windows connection reset
                print(f"⚠️ Request error: {e}")

class KeepAliveHTTPServer(socketserver.TCPServer):
    """HTTP Server that doesn't crash on connection errors"""
    
    allow_reuse_address = True
    request_queue_size = 10
    
    def __init__(self, *args, **kwargs):
        self.timeout = 1  # Check for shutdown every second
        super().__init__(*args, **kwargs)
    
    def server_bind(self):
        """Bind with SO_REUSEADDR to avoid 'Address already in use' errors"""
        import socket
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Set keepalive to prevent connection timeouts
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        super().server_bind()
    
    def handle_error(self, request, client_address):
        """Handle errors gracefully without crashing"""
        import traceback
        exc_type, exc_value, exc_traceback = sys.exc_info()
        
        # Ignore common connection errors
        ignored_errors = [
            'ConnectionResetError',
            'BrokenPipeError', 
            'WinError 10054',
            'ConnectionAbortedError'
        ]
        
        if any(err in str(exc_type) for err in ignored_errors):
            return  # Silently ignore
        
        # Log other errors
        print(f"⚠️ Server error from {client_address}:")
        traceback.print_exc()

def run_server(port=8000):
    """Run the robust HTTP server"""
    
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or '.')
    
    handler = RobustHTTPRequestHandler
    
    try:
        with KeepAliveHTTPServer(("", port), handler) as httpd:
            print(f"🌐 Robust HTTP Server running on http://localhost:{port}")
            print(f"📂 Serving files from: {os.getcwd()}")
            print(f"🔄 Auto-restart enabled (survives connection errors)")
            print(f"⌨️  Press Ctrl+C to stop\n")
            
            # Handle Ctrl+C gracefully
            def signal_handler(sig, frame):
                print("\n\n👋 Shutting down server...")
                httpd.shutdown()
                sys.exit(0)
            
            signal.signal(signal.SIGINT, signal_handler)
            
            # Run server forever
            httpd.serve_forever()
            
    except OSError as e:
        if 'Address already in use' in str(e):
            print(f"❌ Port {port} is already in use!")
            print(f"💡 Try:")
            print(f"   1. Kill existing process: taskkill /F /IM python.exe")
            print(f"   2. Use different port: python http_server.py 8001")
        else:
            raise

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_server(port)