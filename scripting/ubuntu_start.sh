sudo -i
#!/usr/bin/env bash
apt update -y

apt install python3-pip -y 2>/dev/null

pip install lxml

pip install beautifulsoup4

apt install python3-bs4


