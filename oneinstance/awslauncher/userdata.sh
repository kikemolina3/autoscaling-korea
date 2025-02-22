#!/bin/bash

set -e
set -x

apt-get update -y && apt-get install -y python3-pip python3-venv
apt-get update -y && apt-get install -y ffmpeg
apt-get install git -y
apt-get install cargo -y
apt-get install unzip -y

curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

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
aws s3 cp ~/output.log s3://[BUCKET]/[PROGRAM]/[DATE]/execution-results.log

# Terminate the instance itself
token=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
instance_id=$(curl -H "X-aws-ec2-metadata-token: $token" http://169.254.169.254/latest/meta-data/instance-id)
aws ec2 terminate-instances --instance-ids $instance_id