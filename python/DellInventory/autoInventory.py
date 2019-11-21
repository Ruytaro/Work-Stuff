#!/usr/bin/python

"""
File: autoInventory.py
Author: smartin<smartin@sonoc.io>
Version: 1.1

Changelog:
 v1.0 - 2019/10/17 - smartin - Creation.
 v1.1 - 2019/11/21 - smartin - Normalization of mediatype field.

Description: Get the hardware inventory of the server and sends it to the rest
   api in order to keep the inventory database updated with the last state.
"""

from datetime import datetime
import os
from urllib import urlencode
import urllib2
from subprocess import PIPE,Popen

endpoint = 'http://192.168.32.21:3300'

class ServerBoard:
    cpuModel = ""
    cpuThreads = 0
    memoryType = ""
    memoryTotal = 0
    serverModel = ""
    serviceTag = ""
    osFamily = ""
    osVersion = ""
    kernel = ""
    hostname = ""


class MemoryStick:
    partNumber = ""
    capacity = 0
    slot = ""
    speed = 0

class StorageDevice:
    partNumber = ""
    capacity = 0
    formFactor = ""
    slot = ""
    mediaType = ""
    busType = ""


class NetworkInterface:
    macAddress = ""
    ipAddress = ""
    driver = ""
    ifaceName = ""
    inUse = False

board = ServerBoard()
memories = {}
storage = {}
netIfaces = {}
software = {}

def getRacadmInfo():
    info = Popen(['racadm', 'hwinventory'], stdout=PIPE).communicate()[0].split('\n')
    slot = ""
    instanceID = ""
    for line in info:
        if "----" in line:
            instanceID = ""
            slot = ""
        if "[InstanceID:" in line:
            instanceID = line.split(':')[1].strip().strip(']')
            if "Disk" in instanceID:
                if "Virtual" in instanceID.split('.')[1]:
                    slot = "VSD."+instanceID.split('.')[-1].strip()
                else:
                    slot = "HDD."+instanceID.split('.')[-1].strip()
                storage[slot] = StorageDevice()
                storage[slot].slot = slot
                storage[slot].partNumber = "Hardware RAID"
            if "iDRAC" in instanceID:
                slot = "iDRAC"
                netIfaces[slot] = NetworkInterface()
                netIfaces[slot].ifaceName = slot
                netIfaces[slot].inUse = True
        if "CPU" in instanceID:
            if "Model" in line:
                board.cpuModel = line.split('=')[1].strip()
        if "DIMM" in instanceID:
            slot = instanceID.split('.')[-1].strip()
            if not slot in memories:
                memories[slot] = MemoryStick()
                memories[slot].slot = slot
            if "MemoryType" in line:
                board.memoryType = line.split('=')[1].strip()
                memories[slot].busType = line.split("=")[1].strip()
            if "PartNumber" in line:
                memories[slot].partNumber = line.split("=")[-1].strip()
            if "Speed" in line:
                memories[slot].speed = line.split("=")[-1].strip()
            if "Size" in line:
                memories[slot].capacity = line.split("=")[-1].strip().split(' ')[0]
        if "Disk" in instanceID:
            if "BusProtocol" in line:
                storage[slot].busType = line.split("=")[-1].strip()
            if "MediaType" in line:
                mtype = line.split("=")[-1].strip()
                if "solid state" in mtype.lower():
                    mtype = "ssd"
                if "hard disk" in mtype.lower():
                    mtype = "hdd"
                storage[slot].mediaType = mtype
            if "DriveFormFactor" in line:
                storage[slot].formFactor = line.split("=")[-1].strip()
            if "Model" in line:
                storage[slot].partNumber = line.split("=")[-1].strip()
            if line.startswith("SizeInBytes "):
                storage[slot].capacity = int(line.split("=")[-1].strip().split(' ')[0].strip())/1000/1000/1000
            if "RAIDTypes" in line:
                storage[slot].formFactor = line.split("=")[-1].strip()
        if "iDRAC" in instanceID:
            if "PermanentMACAddress" in line:
                netIfaces[slot].macAddress = line.split("=")[-1].strip().upper()
            if "URLString" in line:
                netIfaces[slot].ipAddress = line.split("=")[-1].strip().split(":")[-2].strip('/')
        if "System" in instanceID:
            if "Model" in line:
                board.serverModel = line.split("=")[-1].strip()
            if "ServiceTag" in line:
                board.serviceTag = line.split("=")[-1].strip()



def getDMIDecodeInfo():
    handle = ""
    memory = MemoryStick()
    data = Popen(['dmidecode'], stdout=PIPE).communicate()[0].split('\n')
    for line in data:
        if "Handle " in line:
            if "Memory Dev" in handle:
                try:
                    memories[memory.slot] = memory
                except:
                    pass
            handle = ""
        if handle == "" and not "Handle " in line:
            handle = line
            if "Memory Dev" in handle:
                memory = MemoryStick()
        if "Memory Dev" in handle:
            if "Unknown" in line:
                handle = "asdf"
                memory = MemoryStick()
            if "Type:" in line:
                board.memoryType = line.split(':')[1].strip()
                memory.busType = line.split(':')[1].strip()
            if "Part Number:" in line:
                memory.partNumber = line.split(":")[-1].strip()
            if line.strip().startswith("Speed:") and not "Unknown" in line:
                memory.speed = line.split(":")[-1].strip().split(' ')[0]
            if "Size:" in line and not "No Module" in line:
                memory.capacity = line.split(":")[-1].strip().split(' ')[0]
            if line.strip().startswith("Locator:"):
                memory.slot = line.split(":")[-1].strip()
        if "Processor" in handle:
            if "Version:" in line and not "Not Specified" in line:
                board.cpuModel = line.split(':')[1].strip()
        if "Supermicro" in data:
            if "Base Board" in handle:
                if "Serial Number:" in line:
                    board.serviceTag = line.split(":")[-1].strip()
                if "Product Name:" in line:
                    board.serverModel = line.split(":")[-1].strip()
        else:
             if "System Information" in handle:
                if "Serial Number:" in line:
                    board.serviceTag = line.split(":")[-1].strip()
                if "Product Name:" in line:
                    board.serverModel = line.split(":")[-1].strip()           


def getSysInfo():
    board.hostname = Popen(['hostname'], stdout=PIPE).communicate()[0].strip()
    board.cpuThreads = Popen(['nproc'], stdout=PIPE).communicate()[0].strip()
    memInfo = Popen(['cat', '/proc/meminfo'], stdout=PIPE).communicate()[0].split('\n')
    for line in memInfo:
        if line.startswith("MemTotal:"):
            board.memoryTotal = int(line.split(':')[-1].strip().split(' ')[0])/1024/1024
    osInfo = Popen(['cat', '/etc/os-release'], stdout=PIPE).communicate()[0].split('\n')
    for line in osInfo:
        if line.startswith("ID="):
            board.osFamily = line.split('=')[-1].strip('"')
        if line.startswith("VERSION_ID"):
            board.osVersion = line.split('=')[-1].strip('"')
    board.kernel = Popen(['uname', '-r'], stdout=PIPE).communicate()[0].strip()
    osIface = Popen(['ip', 'address'], stdout=PIPE).communicate()[0].split('\n')
    for line in osIface:
        if "mtu" in line:
            name = line.split(':')[1].strip()
            if not "lo" in name:
                netIfaces[name] = NetworkInterface()
                netIfaces[name].ifaceName = name
                if "UP" in line and not "NO-CARRIER" in line:
                    netIfaces[name].inUse = True
                driverIface = Popen(['ethtool', '-i', name], stdout=PIPE).communicate()[0].split('\n')
                for line in driverIface:
                    if "driver:" in line:
                        netIfaces[name].driver =  line.split(":")[-1].strip()
        if "ether" in line and not "lo" in name:
            netIfaces[name].macAddress = line.strip().split(" ")[1].upper()
        if "inet " in line and not "lo" in name:
            netIfaces[name].ipAddress = line.strip().split(" ")[1].split('/')[0]




def updateInventory():
    timestamp = str(datetime.now())
    hostname = board.hostname
    req = urllib2.Request( endpoint + '/servers?hostname=eq.' + hostname)
    req.add_header('Prefer', 'resolution=merge-duplicates')
    req.get_method = lambda: 'DELETE'
    urllib2.urlopen(req)
    post = "lastupdate=" + timestamp
    for var in vars(board):
        post += str("&" + var + "=" + str(getattr(board,var)))
    req = urllib2.Request( endpoint + '/servers', post.lower())
    req.add_header('Prefer', 'resolution=merge-duplicates')
    urllib2.urlopen(req)
    for i in netIfaces:
        post = str('hostname=' + hostname)
        for var in vars(netIfaces[i]):
            post += "&" + var + "=" + str(getattr(netIfaces[i],var))
        req = urllib2.Request( endpoint + '/interfaces', post.lower())
        req.add_header('Prefer', 'resolution=merge-duplicates')
        urllib2.urlopen(req)
    for i in memories:
        post = str('hostname=' + hostname)
        for var in vars(memories[i]):
            post += "&" + var + "=" + str(getattr(memories[i],var))
        req = urllib2.Request( endpoint + '/memory', post.lower())
        req.add_header('Prefer', 'resolution=merge-duplicates')
        urllib2.urlopen(req)
    for i in storage:
        post = str('hostname=' + hostname)
        for var in vars(storage[i]):
            post += "&" + var + "=" + str(getattr(storage[i],var))
        req = urllib2.Request( endpoint + '/disks', post.lower())
        req.add_header('Prefer', 'resolution=merge-duplicates')
        urllib2.urlopen(req)
    for i in software:
        post = str('hostname=' + hostname)
        for var in vars(software[i]):
            post += "&" + var + "=" + str(getattr(software[i],var))
        req = urllib2.Request( endpoint + '/software', post.lower())
        req.add_header('Prefer', 'resolution=merge-duplicates')
        urllib2.urlopen(req)


try:
    getRacadmInfo()
except:
    getDMIDecodeInfo()

getSysInfo()

updateInventory()
