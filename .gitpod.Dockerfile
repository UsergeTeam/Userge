FROM gitpod/workspace-full-vnc

RUN sudo apt-get update
RUN sudo apt-get install -y \
    libasound2-dev \
    libgtk-3-dev \
    libnss3-dev \
    curl \
    git \
    gnupg2 \
    unzip \
    wget \
    neofetch \
    ffmpeg \
    jq

RUN curl -sO https://cli-assets.heroku.com/install.sh && bash install.sh && rm install.sh

RUN sudo rm -rf /var/lib/apt/lists/*