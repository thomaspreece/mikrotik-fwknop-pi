# mikrotik-fwknop-pi
This repo details how to use a Raspberry PI as an fwknop server which updates address lists on the Mikrotik Router. This is required as Mikrotik do not support fwknop on RouterOS. If your Mikrotik Router supports MetaRouter, you might be able to install OpenWRT and use fwknop on that but I haven't experimented with that so good luck. The main disadvantage of this method is that the fwknop must be on a certain port.  
The way it works is that the Router passes the fwknop packet to the PI. The PI will then validate it and add the provided address to an address list named FWKNOP_PROTO_PORT for the specified time on the router.

## Requirements

### Port Forwarding
Your router needs to pass the fwknop packages through to the PI. This typically requires you to setup a port forward for your fwknop port to your PI and to also allow that port to be forwarded through the firewall.
For example if I'm connecting to my Router from the outside world (eth0), my fwknop is always on udp port 62201 and the PI is at a static address of 192.168.1.50 then running the following commands will allow the packet through the firewall and forward it to my PI.
```
add action=accept chain=forward dst-port=62201 protocol=udp
add action=dst-nat chain=dstnat dst-port=62201 in-interface="Internet PPPoE" \
    protocol=udp to-addresses=192.168.1.50 to-ports=62201
```

### Installing fwknop on the pi
To use the `CMD_CYCLE_OPEN` and `CMD_CYCLE_CLOSE` commands of fwknop you need to be running a version of fwknop-server equal or greater to 2.6.8. At the time of writing Jessie only had 2.6.0 in the repos. It is recommended to upgrade to Stretch to get a new version of fwknop. Alternatively I've had some success with manually installing the fwknop packages from the Stretch repo onto Jessie.
To install fwknop server run:
```
sudo apt-get install fwknop-server
```
You'll also want to install fwnop client as well if you don't have any keys already generated:
```
sudo apt-get install fwknop-client
```

### Mikrotik API User
You'll want to set up a new user on the router with permissions of API and WRITE. This prevents the API user from using winbox or reading settings. Note down the username and password for later.

### Python Dependancies
You'll need python installed and the following dependancies:
```
sudo pip install librouteros
```

Note if you get an error, it might be that your setuptools needs updating:
```
sudo pip install --upgrade setuptools
```

## Setup
Clone this repo into your home directory.

### Generating keys
To generate a new set of keys run
```
fwknop --key-gen
```
Note down KEY_BASE64 and HMAC_KEY_BASE64 for later.

### Editing /etc/fwknop/access.conf
You now need to tell fwknop what to do and what encryption keys to use. You'll want to replace the contents of `/etc/fwknop/access.conf` with the following stanza:
```
SOURCE              ANY
KEY_BASE64          [KEY_BASE64]
HMAC_KEY_BASE64     [HMAC_KEY_BASE64]
CMD_CYCLE_OPEN      python [THIS_REPOS_LOCATION]/open_ports.py --routerip [ROUTER_IP] --routeruser [ROUTER_USER] --routerpass [ROUTER_PASS] $SRC $PROTO $PORT $CLIENT_TIMEOUT
CMD_CYCLE_CLOSE     NONE
```
Make sure you replace [KEY_BASE64], [HMAC_KEY_BASE64] with the keys you noted down in the above section. Also make sure to replace [THIS_REPOS_LOCATION] with the full file path of where you installed this repo. [ROUTER_USER] and [ROUTER_PASS] should be replaced with the information you noted down in the Mikrotik API User section. The [ROUTER_IP] should be replaced with the IP of your router from the network the pi is on.

Below is an example stanza (with fake data in)
```
SOURCE              ANY
KEY_BASE64          1o9pDITqK2aEzeOqo3tQ/6RxsVUNhnw3f6o4cy1ir0c=
HMAC_KEY_BASE64     DrKWSaAcyTwR4dxKYJj44vxITJNbwrhEsU/a2j0xL/oknqj5Zm0Ifv6enxkX7Hy2PPdID91qr6DnGB+9ZPvjTg==
CMD_CYCLE_OPEN      python /home/thomaspreece/mikrotik-fwknop-pi/open_ports.py --routerip 192.168.1.1 --routeruser apiuser --routerpass abc123 $SRC $PROTO $PORT $CLIENT_TIMEOUT
CMD_CYCLE_CLOSE     NONE
```

### Configuring a Client
I use the fwknop2 android client (https://github.com/jp-bennett/Fwknop2). It is available on both Google Play and FDroid, however the FDroid release seems to be out of date so has some bugs in it so I recommend using the one from google play (or compiling it yourself from source).   

Fwknop2 supports passing the KEY_BASE64 and HMAC_KEY_BASE64 via QR code (prevents you having to type it it). There is no documentation on the how to do this in the documentation of fwknop2 but after some code diving the data should be passed by encoding the folling into the QR code:
```
KEY_BASE64:[KEY_BASE64] HMAC_KEY_BASE64:[HMAC_KEY_BASE64]
```
E.g.
```
KEY_BASE64:1o9pDITqK2aEzeOqo3tQ/6RxsVUNhnw3f6o4cy1ir0c= HMAC_KEY_BASE64:DrKWSaAcyTwR4dxKYJj44vxITJNbwrhEsU/a2j0xL/oknqj5Zm0Ifv6enxkX7Hy2PPdID91qr6DnGB+9ZPvjTg==
```
There are several tools for generating QR codes. For example https://pypi.python.org/pypi/PyQRCode. It won't be detailed here.

Whilst in the app, press the menu button then "New Config" to create a new configuration. To load in the QR code with keys, click menu button and "Capture qr". To save the configuration click menu button and "Save config".

### Setup Your Routing Rules
If everything is working you should be able to issue a fwknop to the router and it should pass it to the PI, the PI should validate it and execute the python script to add the provided IP to an address list FWKNOP_PROTO_PORT on the router. You will still need to do routing on the router to do something special with packets that are in these special FWKNOP_PROTO_PORT address lists for it to actually be useful mind. 
