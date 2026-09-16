"""Local verification server only; never included in the upload ZIP."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(Path(__file__).resolve().parents[1]/'minitool-dist'),**kwargs)
    def end_headers(self):
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self'; connect-src 'none'; worker-src 'none'; object-src 'none'; frame-src 'none'")
        self.send_header('Cache-Control','no-store')
        super().end_headers()
ThreadingHTTPServer(('127.0.0.1',5191),Handler).serve_forever()
