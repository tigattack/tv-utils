#! /bin/sh -e
start=$(date +%s)

apt update > /dev/null

cd /usr/src

echo "***** build time can be up to 30 minutes. *****"

DATE=$(date +%Y%m%d)
MACHINE=$(uname -m)

echo "installing librepfunc-git"
git clone https://github.com/wirbel-at-vdr-portal/librepfunc.git
cd librepfunc

make install

mkdir -p ./usr/lib/pkgconfig
mkdir -p ./usr/include
mkdir -p ./usr/
mkdir -p ./usr/doc
mkdir -p ./usr/man1

install -m 755 librepfunc.so* ./usr/lib
install -m 644 repfunc.h      ./usr/include
install -m 644 COPYING README ./usr/doc
install -m 644 librepfunc.pc  ./usr/lib/pkgconfig

cd ..
tar -cjf librepfunc-$DATE-binary-$MACHINE.tar.bz2 librepfunc/usr
mv -v librepfunc-$DATE-binary-$MACHINE.tar.bz2 /build

echo "installing w_scan_cpp-git"

git clone https://github.com/wirbel-at-vdr-portal/w_scan_cpp.git
cd w_scan_cpp

git -c advice.detachedHead=false checkout ${W_SCAN_CPP_VERSION}

if [ ${WIRBELSCAN_VERSION} != "default" ] ; then
   echo "overriding WIRBELSCAN_VERSION with ${WIRBELSCAN_VERSION}"
   sed -i -E "s/(WIRBELSCAN_VERSION = wirbelscan-).*/\1${WIRBELSCAN_VERSION}/" Makefile
fi

make download
make install
make binary
mv -v w_scan_cpp-20*-binary* /build

stop=$(date +%s)
runtime=$((stop-start))

echo "***** END: script runtime was $runtime seconds. *****"
