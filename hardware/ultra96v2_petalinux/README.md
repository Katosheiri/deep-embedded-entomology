# Ultra96v2 - Petalinux

Petalinux is another framework than Pynq that we can use to run a DPU. This allows us to run code in different languages, specifically in Python and C++.

## Setup the board

### 1. Create SD Card Image

The first step is to setup the SD Card Image. This image can be found [here](https://www.hackster.io/AlbertaBeef/vitis-ai-2-0-flow-for-avnet-vitis-platforms-06cfd6) or [here](https://avtinc.sharepoint.com/teams/ET-Downloads/Shared%20Documents/Forms/AllItems.aspx?id=%2Fteams%2FET%2DDownloads%2FShared%20Documents%2Fxtm%5Fteam%2Fbergeron%2FVITIS%2Fvitis%5Fai%5F2%5F0%5Favnet%2Favnet%2Du96v2%5Fsbc%5Fbase%2Dv2021%2E2%2Ddpu%2Dv2%2E0%2E0%2D2022%2D02%2D02%2Ezip&parent=%2Fteams%2FET%2DDownloads%2FShared%20Documents%2Fxtm%5Fteam%2Fbergeron%2FVITIS%2Fvitis%5Fai%5F2%5F0%5Favnet&p=true&ga=1) (direct link to download).

Flash your SD card with this image using Balena Etcher.

Insert the card in the board and boot it.

### 2. Debug USB ethernet connection

The flow to connect to the board is detailed [here](https://ultra96-pynq.readthedocs.io/en/latest/getting_started.html). You can connect via wifi or USB. This section details what to do to connect via USB.

Note that the board might not have an IP adress. To verify it :
```
ifconfig
```

if the inet IP adress doesn't show or is different than ```192.168.3.2```, use this command :
```
sudo ifconfig board_name_in_ifconfig 192.168.3.2 netmask 255.255.255.0 up
```

You will then be set up to connect to the board via ssh :
```
ssh root@192.168.3.1
password root
```

### 3. Work on the board

Every time you will boot the board, you will need to source this file :
```
cd ~/dpu_sw_optimize/zynqmp
source ./zynqmp_dpu_optimize.sh
```

Our advice is to work in sshfs. This allows you to code on your computer with your IDE of choice. To do so, open a terminal :
```
sshfs root@192.168.3.1:/home/root/ /destination/folder/on/your/computer
```

### 4. Examples

You will find some code examples in the ```~/Vitis-AI/demo/VART/``` folder on your board. Note that all codes are not working properly since this Petalinux image is a few yeard old.

Congratulations, you are all set to start using your AI application !