import string
import flask
import subprocess
import os 
import random

app = flask.Flask(__name__)

action = "web"

@app.route("/compilation", methods=["GET"])
def compile():
    try:
        target_dir = "./target-" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))
        os.chdir(action)
        os.mkdir(target_dir)
        command = f"CARGO_TARGET_DIR={target_dir} cargo build && CARGO_TARGET_DIR={target_dir} cargo clean"
        subprocess.Popen(command, shell=True)
        os.chdir("..")
        return "Compilation started"
    except FileNotFoundError:
        return "Directory not found", 404

if __name__ == "__main__":
    app.run(port=5000)

