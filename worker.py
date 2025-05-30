import json
import requests
from PyQt5.QtCore import QThread, pyqtSignal

class OllamaWorker(QThread):
    result_ready = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, conversation):
        super().__init__()
        self.conversation = conversation

    def run(self):
        try:
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": "llama3",
                    "messages": self.conversation,
                    "stream": True
                },
                stream=True
            )
            full_reply = ""
            for line in response.iter_lines():
                if line:
                    data = json.loads(line.decode("utf-8"))
                    full_reply += data.get("message", {}).get("content", "")
            self.result_ready.emit(full_reply.strip())

        except Exception as e:
            self.error.emit(str(e))
