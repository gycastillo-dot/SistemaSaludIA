import webbrowser
from threading import Timer
from app import app

def abrir_navegador():
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    Timer(2, abrir_navegador).start()
    app.run(host="127.0.0.1", port=5000, debug=False)