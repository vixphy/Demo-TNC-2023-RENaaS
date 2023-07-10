#!/bin/bash

echo this script will install freeRouter on your computer.
echo WARNiNG: this will wipe your current network settings!
echo prerequisites: minimal debian sid and root rights.

# read -p "type yes to continue: " RESP
# if [[ "$RESP" != "yes" ]] ; then
#   echo aborting
#   exit
#   fi



installPackage()
{
echo ""
echo ""
echo ""
echo ""
echo --------------------------------------------- installing $1...
DEBIAN_FRONTEND=noninteractive apt-get -f -y install $1
}



DEBIAN_FRONTEND=noninteractive apt-get update
DEBIAN_FRONTEND=noninteractive apt-get -f -y dist-upgrade

for PKG in 8 9 10 11 12 13 14 15 16 17 18 19; do
  installPackage openjdk-$PKG-jre-headless
  done

for PKG in default-jre-headless socat ethtool iproute2 net-tools bwm-ng; do
  installPackage $PKG
  done

for PKG in openvswitch-switch dpdk dpdk-dev libpcap-dev openssl libssl-dev libbpf-dev bpftool libmnl-dev; do
  installPackage $PKG
  done

for PKG in rfkill iw wireless-tools wireless-regdb hostapd wpasupplicant; do
  installPackage $PKG
  done

for PKG in default-jdk-headless llvm clang gcc psmisc zip unzip wget curl mc sudo memtester psmisc busybox; do
  installPackage $PKG
  done

for PKG in graphviz telnet openssh-client tshark nmap iperf iperf3; do
  installPackage $PKG
  done

for PKG in qemu qemu-system vlc mplayer ffmpeg youtube-dl gmediarender; do
  installPackage $PKG
  done

for PKG in apparmor cloudinit; do
  echo ""
  echo ""
  echo ""
  echo ""
  echo --------------------------------------------- removing $1...
  DEBIAN_FRONTEND=noninteractive apt-get -f -y remove $1
  done

TRG=/rtr
TMP=~/install.rtr

mkdir -p $TMP
cd $TMP/
wget www.freertr.org/rtr.zip
unzip -o rtr.zip > /dev/null
wget -O $TMP/misc/default.cfg www.freertr.org/install-sw.txt
cd $TMP/src/
./d.sh
wget www.freertr.org/rtr.ver
wget www.freertr.org/rtr.jar
cd $TMP/binImg/
wget www.freertr.org/rtr-`uname -m`.tar
cd $TMP/binTmp/
tar xf ../binImg/rtr-`uname -m`.tar
cd $TMP/misc/service/
./c.sh $TRG

cat > $TRG/update.sh << EOF
#!/bin/sh
sudo apt-get update
sudo apt-get dist-upgrade
sudo apt-get remove apparmor
sudo apt-get autoremove
sudo apt-get clean
sudo sync
sudo fstrim -v -a -m 1M
#sudo e4defrag /
EOF
chmod +x $TRG/update.sh

sync

echo installation finished! review the generated files at $TRG and reboot!
echo after it, you have to telnet 10.255.255.254 to access your router!
