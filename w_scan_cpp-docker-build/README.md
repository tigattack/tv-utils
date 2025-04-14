# w_scan_cpp build

This directory contains the files to build [w_scan_cpp](https://www.gen2vdr.de/wirbel/w_scan_cpp/index2.html) ([GitHub](https://github.com/wirbel-at-vdr-portal/w_scan_cpp)) and the required [librepfunc](https://github.com/wirbel-at-vdr-portal/librepfunc) in Docker.

The build script is based on https://github.com/wirbel-at-vdr-portal/w_scan_cpp-binaries/blob/master/build-w_scan_cpp.sh

## Usage

> [!TIP]
> You may include the `W_SCAN_CPP_VERSION` environment variable if you wish to build a specific version, or omit it if you wish to build from w_scan_cpp's master branch.

```
docker build . w_scan_cpp_build
docker run --rm \
  -e W_SCAN_CPP_VERSION=20231015 \
  -v ./result:/build \
  w_scan_cpp_build
```

You'll find the compiled binaries in `./result`.

At time of creation, I had to override the version of [wirbelscan](https://www.gen2vdr.de/wirbel/wirbelscan/index2.html) included in the w_scan_cpp build due to a compilation error, so I actually did this:

```
docker build . w_scan_cpp_build
docker run --rm \
  -e W_SCAN_CPP_VERSION=20231015 \
  -e WIRBELSCAN_VERSION=2024.09.15 \
  -v ./result:/build \
  w_scan_cpp_build
```

## Disclaimer

I use it on a Raspberry Pi 4 and it works well. However I make no guarantees of full functionality, nor do I plan to support this.
