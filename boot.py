from machine import reset
from network import WLAN, STA_IF, phy_mode, MODE_11N
from time import ticks_ms
import gc
import webrepl
import ujson as json
from socket import socket, AF_INET, SOCK_DGRAM, IPPROTO_UDP, getaddrinfo
from esp32 import raw_temperature

STA_CONF_ARR_PATH = "/sta_conf_arr.json"
PHY_MODE = MODE_11N
STA_CONNECT_TIMEOUT = 10000

AF_INET_BROADCAST = "255.255.255.255"
ADDR_ANNOUNCE_PORT = 1337

def get_active_sta_if():
    sta_if = WLAN(STA_IF)
    if not sta_if.active():
        phy_mode(PHY_MODE)
        sta_if.active(True)
    return sta_if

def deactivate_sta_if():
    sta_if = WLAN(STA_IF)
    sta_if.active(True)
    sta_if.connect("", "")
    sta_if.active(False)

def scan_wifi():
    sta_if = get_active_sta_if()
    scan = sta_if.scan()
    print("\nWiFi Scan:\n\t{:35}, {:14}, {:2}, {:4}, {:4}, {:6}".format("ssid", "bssid", "ch", "rssi", "auth", "hidden"))
    for ssid, bssid, channel, rssi, authmode, hidden in scan:
        print("\t{:35}, 0x{:12}, {:2}, {:4}, {:4}, {:6}".format(ssid, "".join(["{:02x}".format(b) for b in bssid])[:-1], channel, rssi, authmode, hidden))
    print("")
    return scan

def connect_to_ap(ssid, psk):
    sta_if = get_active_sta_if()
    sta_if.connect(ssid, psk)
    now = ticks_ms()
    while (not sta_if.isconnected()) and ((ticks_ms()-now < STA_CONNECT_TIMEOUT)):
        pass
    if not sta_if.isconnected():
        raise OSError("Could not connect to AP")

def connect_to_wifi():
    sta_conf_arr = json.load(open(STA_CONF_ARR_PATH))
    for ssid, _, _, _, _, _ in scan_wifi():
        for sta_conf in sta_conf_arr:
            if ssid.decode() == sta_conf["ssid"]:
                print("Connecting to "+sta_conf["ssid"])
                try:
                    connect_to_ap(sta_conf["ssid"], sta_conf["psk"])
                except OSError as e:
                    pass
                else:
                    print("Connected to "+sta_conf["ssid"])
                    return
    deactivate_sta_if()
    raise OSError("No access point available.")

def udp_broadcast_address():
    s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
    s.connect((AF_INET_BROADCAST, ADDR_ANNOUNCE_PORT))
    s.send("{}\n".format(WLAN().ifconfig()[0]))
    s.close()

if __name__ == '__main__':
    try:
        connect_to_wifi()
        udp_broadcast_address()
        webrepl.start()
    except KeyError as err:
        print("Key Error: {0}".format(err))
    except OSError as err:
        print("OS Error: {0}".format(err))
    gc.collect()
