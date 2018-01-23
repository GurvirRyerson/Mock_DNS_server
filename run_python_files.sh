#!/bin/sh

cd /home/cps706/dnsdir
python dnsdir/local_DDNS_python.py &
python dnsdir/hiscinema_DDNS.py &
python dnsdir/herCDN_DDNS.py &
python herCDN_server.py &
python hiscinema_webserver.py
