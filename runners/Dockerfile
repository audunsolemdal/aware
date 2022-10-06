FROM summerwind/actions-runner:latest

RUN sudo wget -q https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb
RUN sudo dpkg -i packages-microsoft-prod.deb
RUN sudo apt update -y && sudo apt install -y powershell && sudo rm -rf /var/lib/apt/lists/*