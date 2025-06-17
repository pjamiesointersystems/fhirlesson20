from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    print(">>> Inside root route <<<")  # Breakpoint here
    return "Hello from Flask"

if __name__ == "__main__":
    print(">>> Flask is starting <<<")  # This should print in debug console
    app.run()