FROM debian:bookworm-slim

ARG DEBIAN_FRONTEND=noninteractive

# Will build w_scan_cpp from master branch if left as 'master'.
ENV W_SCAN_CPP_VERSION=master
# Will use the version defined in w_scan_cpp's Makefile if left as 'default'.
ENV WIRBELSCAN_VERSION=default

RUN apt update &&\
    apt install -y --no-install-recommends \
        # Setup deps
        ca-certificates \
        curl \
        # Build deps
        build-essential \
        git \
        libcap-dev \
        libcurl4-openssl-dev \
        libfontconfig-dev \
        libfreetype-dev \
        libjpeg62-turbo-dev \
        libpugixml-dev \
        pkg-config \
        wget &&\
    rm -rf /var/lib/apt/lists/*

COPY build-w_scan_cpp.sh /app/build-w_scan_cpp.sh
RUN chmod +x /app/build-w_scan_cpp.sh

WORKDIR /build
VOLUME /build

CMD ["/app/build-w_scan_cpp.sh"]
