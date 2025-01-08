#!/bin/bash

set -e
set -x

apt-get update -y && apt-get install -y python3-pip python3-venv
apt-get update -y && apt-get install -y ffmpeg
apt-get install git -y
apt-get install cargo -y

# Clone the repository
git clone https://kikemolina3:[GH_TOKEN]@github.com/kikemolina3/autoscaling-korea.git

# Add the cargo bin directory to the PATH
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

cd autoscaling-korea
python3 -m venv venv
source venv/bin/activate
echo "source /autoscaling-korea/venv/bin/activate" >> ~/.bashrc

cd oneinstance
pip3 install -e .

# Install dependencies
cd compilation/web
cargo fetch
cd ../..

# Run the application
python3 app.py &

python3 main.py --program [PROGRAM] --duration [DURATION] >> ~/output.log

# Store the output in S3
DATE=$(date '+%Y-%m-%d-%H-%M-%S')
aws s3 cp ~/output.log s3://[BUCKET]/[PROGRAM]-$DATE.log