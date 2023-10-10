from argparse import ArgumentParser
from http.server import HTTPServer

from human_interface.web.request_handler import RequestHandler
from human_interface.web.action_handler import init_action_handler

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--port", type=int, default=8888)
    parser.add_argument("--screen-size", type=int, default=512)
    parser.add_argument("--agent-num", type=int, default=2)
    args = parser.parse_args()

    init_action_handler(args.screen_size, args.agent_num)
    server = HTTPServer(("127.0.0.1", args.port), RequestHandler)
    print("Server running at 127.0.0.1:" + str(args.port))
    server.serve_forever()