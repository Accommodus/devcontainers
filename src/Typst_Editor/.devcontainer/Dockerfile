ARG BASE_IMAGE="debian:bookworm"
ARG FONT_HOLDING_PATH="/root/typst_container"
ARG FONT_DESTINATION_PATH="/usr/local/share/fonts"

FROM ${BASE_IMAGE} AS builder
ARG FONT_HOLDING_PATH
ARG WORKSPACE="/root/install"

WORKDIR ${WORKSPACE}
ADD https://github.com/google/fonts/archive/main.tar.gz gfonts.tar.gz
RUN tar -xf gfonts.tar.gz
RUN mkdir -p ${FONT_HOLDING_PATH}/goog/ \
    && mv ${WORKSPACE}/fonts-main/ofl/ ${FONT_HOLDING_PATH}/goog/

RUN apt-get update \
    && apt-get install -y --no-install-recommends unzip
ADD https://github.com/githubnext/monaspace/releases/download/v1.200/monaspace-v1.200.zip mona.zip
RUN unzip -j mona.zip '*.otf' '*.ttf' -d ${FONT_HOLDING_PATH}/mona/

FROM ${BASE_IMAGE}
ARG FONT_HOLDING_PATH
ARG FONT_DESTINATION_PATH

RUN apt-get update \
    && apt-get install -y --no-install-recommends fontconfig \
    && rm -rf /var/lib/apt/lists/*
    
WORKDIR ${FONT_DESTINATION_PATH}
COPY --from=builder ${FONT_HOLDING_PATH} ./
RUN fc-cache -f