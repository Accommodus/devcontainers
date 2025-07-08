FROM mcr.microsoft.com/devcontainers/base:ubuntu

RUN apt-get update && apt-get install -y g++ curl tar git openssl

USER vscode

RUN curl https://nim-lang.org/choosenim/init.sh -sSf | sh -s -- -y
ENV PATH="/home/vscode/.nimble/bin:${PATH}"

WORKDIR /home/vscode
RUN nimble refresh -y
RUN nimble install -y nimlangserver