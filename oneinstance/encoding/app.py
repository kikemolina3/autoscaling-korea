import random
import string
from flask import Flask
import subprocess

app = Flask(__name__)

@app.route('/encoding', methods=['GET'])
def encode_video():
    input_path = 'video.mp4'
    output_path = 'output_video-' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=7)) + '.mp4'

    command = f"ffmpeg -i {input_path} -vcodec libx264 {output_path} && rm {output_path}"
    subprocess.Popen(command, shell=True)

    return "Encoding started"

if __name__ == '__main__':
    app.run(debug=True)
