#!/bin/bash

set -e
set -x

sudo apt-get update -y && sudo apt-get install -y python3-pip python3-venv
sudo apt-get update -y && sudo apt-get install -y ffmpeg
sudo apt-get install git -y

# Clone the repository
git clone "https://kikemolina3:<GH_TOKEN>@github.com/kikemolina3/autoscaling-korea.git"

# Download the latest version of Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Add the cargo bin directory to the PATH
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

cd autoscaling-korea
python3 -m venv venv
source venv/bin/activate
echo "source ~/autoscaling-korea/venv/bin/activate" >> ~/.bashrc

cd oneinstance
pip3 install -e .

# Install dependencies
cd compilation/web
cargo fetch
cd ../..

# Run the application
python3 app.py &

python3 main.py --program "compilation" --duration 30 >> ~/compilation.log
python3 main.py --program "encoding" --duration 30 >> ~/encoding.log