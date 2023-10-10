from http.server import BaseHTTPRequestHandler
from pathlib import Path
from human_interface.web.action_handler import Action, get_action_handler
import json

class RequestHandler(BaseHTTPRequestHandler):
    def accept_header(self, content_type="text/html"):
        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.end_headers()
    
    def get_post_json(self):
        content_length = int(self.headers['Content-Length'])
        data = self.rfile.read(content_length)
        return json.loads(data.decode())
    
    def do_GET(self):
        action_handler = get_action_handler()
        print(action_handler)
        
        if self.path == "/":
            self.accept_header()
            self.wfile.write(get_template(
                observation=json.dumps(action_handler.obs),
                screen_size=action_handler.screen_size,
            ))
            
        elif self.path.startswith("/first_person_img"):
            self.accept_header()
            self.wfile.write(Path("human_interface", "log", "first_person_img.png").read_bytes())
        
        elif self.path.startswith("/js/main.js"):
            self.accept_header()
            self.wfile.write(Path("human_interface", "web", "main.js").read_bytes())
            
        else:
            self.send_error(404)
    
    def do_POST(self):
        action_handler = get_action_handler()
        
        if self.path.startswith("/action/"):
            for action in Action.ACTIONS:
                if self.path.startswith("/action/" + action):
                    param = self.get_post_json()
                    param["type"] = Action.INDEX[action]
                    
                    err = action_handler.act(param)
                    if err is not None:
                        self.send_error(400, err)
                    
                    self.accept_header("application/json")
                    self.wfile.write(json.dumps(action_handler.obs).encode())
                    return
            self.send_error(400, f"No such action: {action}")
            
        else:
            self.send_error(404)

def get_template(**kwargs):
    text = Path("human_interface", "web", "template.html").read_text()
    for key in kwargs:
        text = text.replace("$" + key.upper(), str(kwargs[key]))
    return text.encode()