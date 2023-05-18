sudo sytemctl disable nvzramconfig
sudo fallocate -l 4G /mnt/4GB.swap
sudo chmod 600 /mt/4GB.swap
sudo mkswap /mnt/4GB.swap
sudo vi /etc/fstab