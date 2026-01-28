from http.server import BaseHTTPRequestHandler, HTTPServer


class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            message = "Главная страница"

        elif self.path == "/health":
            self.send_response(200)
            message = "OK"

        elif self.path == "/user":
            self.send_response(200)
            message = "Пользователь не авторизован"

        else:
            self.send_response(404)
            message = "Не найдено"

        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(message.encode("utf-8"))


server = HTTPServer(("localhost", 8000), SimpleHandler)
print("Сервер запущен на http://localhost:8000")
server.serve_forever()

