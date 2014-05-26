CGMinerMobileAdapter
=========

Updated version of Hazado's BFGMobileAdapter fork.

Installation (installs in /opt/CGMinerMobileAdapter, and forces system to run it on startup):

    git clone https://github.com/Axadiw/CGMinerMobileAdapter.git
    cd CGMinerMobileAdapter
    ./install.sh

Changes (since BFGMobileAdapter):

- remote commands support (START/STOP/RESTART)
- removed script freezes
- reports configured pools & current coin to MobileMiner
- supports switching between configured pools from MobileMiner UI

Tested on BAMT, CGminer and it's forks (vertminer, sgminer).

If you'd like to donate, please use this account: 1MkmUGJtffLYeFrWSgtewGvWeP1MncnVCt

=========
ORIGINAL README:

UPDATE - apparently this script also works with CGMiner due to their shared implementation of RPC. I may have to rename this thing. 

This is a simple Python Script to take data from the BFGMiner and/or CGMiner RPC and send it to the MobileMiner Apps' REST API.
For more info on the MobileMiner suite of Monitoring and Control Apps, check out http://www.mobileminerapp.com/

Right now this script only posts data to the API for monitoring and does not allow for remote Miner control.
It is currently set for a time-interval of 30 seconds between POSTs to the API.  This is configurable from within the script.


Thanks to <a href="http://www.nwoolls.com/">Nate Woolls</a> - author of MultiMiner and the MobileMiner Apps for IOS and Android, & soon Windows Mobile

Parts are originally derived from Christian Berendt's api-example.py for BFGMiner for the BFGMiner RPC Portion of the script.

<a href="https://github.com/jedimstr/BFGMobileAdapter/wiki/Release-Notes"><b>Release Notes available here.</b></a> 

