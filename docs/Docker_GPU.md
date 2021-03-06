# Docker Usage (GPU version)

This document describes how to setup and use Docker. The following commands were executed on an Ubuntu 16.04 base installation on an EC2 instance on AWS. The GPU version requires the installation of Nvidia GPU drivers.


## Install general programs

```
# update
sudo apt-get update

# install some basics
sudo apt-get install -y build-essential git python-pip libfreetype6-dev \
 libxft-dev libncurses-dev libopenblas-dev gfortran \
 libblas-dev liblapack-dev libatlas-base-dev \
 linux-headers-generic linux-image-extra-virtual unzip \
 swig unzip wget pkg-config zip g++ zlib1g-dev \
 screen
```

## Docker Installation

```
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
sudo apt-get update
sudo apt-get install docker-ce

# test installation
sudo docker run hello-world
```

## Nvidia Driver / Docker installation

From (https://github.com/NVIDIA/nvidia-docker/wiki/Driver-containers-(EXPERIMENTAL))

```
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/ubuntu16.04/nvidia-docker.list \
  | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo sed -i 's/^#root/root/' /etc/nvidia-container-runtime/config.toml

sudo tee /etc/modules-load.d/ipmi.conf <<< "ipmi_msghandler"
sudo tee /etc/modprobe.d/blacklist-nouveau.conf <<< "blacklist nouveau"
sudo tee -a /etc/modprobe.d/blacklist-nouveau.conf <<< "options nouveau modeset=0"
sudo update-initramfs -u

sudo reboot

sudo docker run -d --name nvidia-driver --privileged --pid=host -v /run/nvidia:/run/nvidia:shared \
  nvidia/driver:396.37-ubuntu16.04 --accept-license

# Verify installation (wait ca. 30 seconds)
sudo docker run --runtime=nvidia --rm nvidia/cuda:9.0-base nvidia-smi
```


## Build Container

This builds the GPU version of the container.

```
# install docker container
mkdir ~/code
cd ~/code
git clone https://github.com/marco-willi/camera-trap-classifier.git
cd camera-trap-classifier
sudo docker build . -f Dockerfile.gpu -t camera_trap_classifier
```

## Start Container

Now we run the container and map /my_data/ from the host computer to /data/ inside the container. It is important to adapt these paths to where the actual data is on the host.

```
# run docker image
# maps /my_data/ on host to /data/ in container
sudo docker run --rm --name ctc --runtime=nvidia -v /my_data/:/data/ -itd camera_trap_classifier
# sudo docker run --rm --name ctc --runtime=nvidia -v /home/ubuntu/data/:/data/ -itd camera_trap_classifier
```

## Run Scripts

```
# run scripts with data on host
sudo docker exec ctc ctc.create_dataset_inventory dir -path /data/images \
-export_path /data/dataset_inventory.json

# create directory for tfr-files on host
sudo mkdir /my_data/tfr_files

# create tfr-files
sudo docker exec ctc ctc.create_dataset -inventory /data/dataset_inventory.json \
-output_dir /data/tfr_files/ \
-image_save_side_max 200 \
-split_percent 0.5 0.25 0.25 \
-overwrite


# create directory for log files and model saves
sudo mkdir /my_data/run1 /my_data/save1

# train model
sudo docker exec ctc ctc.train \
-train_tfr_path /data/tfr_files/ \
-val_tfr_path /data/tfr_files/ \
-test_tfr_path /data/tfr_files/ \
-class_mapping_json /data/tfr_files/label_mapping.json \
-run_outputs_dir /data/run1/ \
-model_save_dir /data/save1/ \
-model small_cnn \
-labels class \
-batch_size 16 \
-n_cpus 4 \
-n_gpus 0 \
-buffer_size 16 \
-max_epochs 70 \
-color_augmentation full_randomized

# predict from model
sudo docker exec ctc ctc.predict \
  -image_dir /data/images \
  -results_file /data/output.csv \
  -model_path /data/save1/best_model.hdf5 \
  -class_mapping_json /data/save1/label_mappings.json \
  -pre_processing_json /data/save1/image_processing.json

# export model
sudo mkdir /my_data/save1/my_model_exports/ /my_data/save1/my_estimators/
sudo docker exec ctc ctc.export -model /data/save1/best_model.hdf5 \
  -class_mapping_json /data/save1/label_mappings.json \
  -pre_processing_json /data/save1/image_processing.json \
  -output_dir /data/save1/my_estimators/ \
  -estimator_save_dir /data/save1/my_estimators/keras/

```


## Example with Cats vs Dogs data

```
# start container and map directories
sudo docker run --rm --name ctc --runtime=nvidia -v /home/ubuntu/data/:/data/ -itd camera_trap_classifier

# get sample data from (https://www.microsoft.com/en-ca/download/details.aspx?id=54765)
cd ~/data/
sudo wget -O images.zip "https://download.microsoft.com/download/3/E/1/3E1C3F21-ECDB-4869-8368-6DEBA77B919F/kagglecatsanddogs_3367a.zip"
sudo unzip -q images.zip

# create dataset inventory
sudo docker exec ctc ctc.create_dataset_inventory dir -path /data/PetImages/ \
-export_path /data/dataset_inventory.json

# create directory for tfr-files on host
sudo mkdir /home/ubuntu/data/tfr_files

# create tfr-files
sudo docker exec ctc ctc.create_dataset -inventory /data/dataset_inventory.json \
-output_dir /data/tfr_files/ \
-image_save_side_max 200 \
-split_percent 0.9 0.05 0.05 \
-overwrite

# create directory for log files and model saves
sudo mkdir /home/ubuntu/data/run1 /home/ubuntu/data/save1

# train model
sudo docker exec ctc ctc.train \
-train_tfr_path /data/tfr_files/ \
-val_tfr_path /data/tfr_files/ \
-test_tfr_path /data/tfr_files/ \
-class_mapping_json /data/tfr_files/label_mapping.json \
-run_outputs_dir /data/run1/ \
-model_save_dir /data/save1/ \
-model small_cnn \
-labels class \
-batch_size 128 \
-n_cpus 4 \
-n_gpus 1 \
-buffer_size 512 \
-max_epochs 70 \
-color_augmentation full_randomized
```
