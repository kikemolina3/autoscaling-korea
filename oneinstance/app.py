import random
import string
from flask import Flask
import subprocess
import os

app = Flask(__name__)

@app.route('/encoding', methods=['GET'])
def encode_video():
    input_path = 'encoding/video.mp4'
    output_path = 'output_video-' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=7)) + '.mp4'

    command = f"ffmpeg -i {input_path} -vcodec libx264 {output_path} && rm {output_path}"
    subprocess.Popen(command, shell=True)

    return "Encoding started"

action = "web"

@app.route("/compilation", methods=["GET"])
def compile():
    try:
        target_dir = "./target-" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))
        os.chdir("compilation/" + action)
        os.mkdir(target_dir)
        command = f"CARGO_TARGET_DIR={target_dir} cargo build && CARGO_TARGET_DIR={target_dir} cargo clean"
        subprocess.Popen(command, shell=True)
        os.chdir("../..")
        return "Compilation started"
    except FileNotFoundError:
        return "Directory not found", 404

if __name__ == '__main__':
    app.run(debug=True)
