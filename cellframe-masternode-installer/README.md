# Cellframe Masternode Installer

Cellframe Mastenode installation script will install Cellframe Node to your computer and configure a master role in selected network. 

* Compatible with Cellframe Node 5.3
* Supports Debian and it's derivatives (e.g. Ubuntu)
* Supports amd64, arm64 and armhf architectures

We attempted to include as minimal as possible user input in it. However, some info will need to be provided during the installation. 
Keep an eye out for it!

## What is required for the masternode?

1. A machine that will stay running 24/7
2. Public IP address and open port 8079.
3. Wallet with enough m-tokens to start a masternode. 

For manual masternode configuration, visit wiki.cellframe.net

Link: https://wiki.cellframe.net/02.+Learn/Cellframe+Node/Master+Node+Manual+Setup


## How to begin masternode configuration? 

Run CMI.sh script with a desired network as a parameter. If network name is not provided, Backbone will be selected by default.

Example:
- bash CMI.sh -n Backbone
- bash CMI.sh -n KelVPN

Additionally, an option to provide a link to cellframe-node .deb file is available. 
If not provided, latest available release will be used.

Example:
- bash CMI.sh -n Backbone -l https://pub.cellframe.net/linux/cellframe-node/master/cellframe-node-5.3-342-rwd-amd64.deb

## Configuration process

Cellframe Mastenode installation script will attempt to locate a .dwallet file in the same directory where it is located. 
We recommend to use this option and copy the wallet file prior to launching the script. 

Alternatively, seed phrase (24 words + password) can be used to restore the wallet that was created in Cellframe Dashboard.

While the script is running, it is expected for the selected network to synchronize. Depending on the internet connection, this may take a while. 
We recommend to launch the script using the screen application. 

Install it:
- apt install screen

Read about it in the manual: 
- man screen

## Contact info

In case any issues are encountered during the masternode configuration, contact the original author of the script or Cellframe Support team.

Originally created by hyttmi
- @CELLgainz in Twitter and Cellframe Telegram channels

Cellframe Support group in Telegram: https://t.me/cellframetechsupport

Cellframe Support e-mail address: tech_support@demlabs.net
