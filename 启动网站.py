from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path
import webbrowser
root=Path(__file__).resolve().parent/'yingxian-pagoda'/'dist'
handler=partial(SimpleHTTPRequestHandler,directory=str(root))
server=ThreadingHTTPServer(('127.0.0.1',0),handler)
url=f'http://127.0.0.1:{server.server_port}'
print(f'应县木塔网站已启动：{url}\n关闭此窗口或按 Ctrl+C 停止。',flush=True)
webbrowser.open(url)
try:server.serve_forever()
except KeyboardInterrupt:server.server_close()
