#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, ConfigParser, tarfile, socket, time, scp, paramiko

config = ConfigParser.ConfigParser()
config.read("FiBa.conf")

dirs_files = []

for s in config.sections():
    if s == 'Server':
        serverName = config.get(s, 'Name')
        serverUrl = config.get(s, 'Url')
        serverPort = int(config.get(s, 'Port'))
        serverUser = config.get(s, 'User')
        serverKey = paramiko.RSAKey.from_private_key_file(config.get(s, 'Key'))
    elif s == 'Archive':
        archiveName = '/tmp/' + config.get(s, 'Name') + '_' + socket.gethostname().split('.')[0] + '_' + time.strftime("%Y%m%d%H%M%S") + '.tar.gz'
    else:
        infoName = s
        path = config.get(s, 'Path').split()
        dirs_files.append( (infoName, path, ) )

tar = tarfile.open(archiveName, "w:gz")

for infoName, fileList in dirs_files:
    for f in fileList:
        print infoName + ' : ' + f
        tar.add(f)

tar.close()

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname = serverUrl, port = serverPort, username = serverUser, pkey = serverKey)
trans = scp.SCPClient(client.get_transport())
trans.put(archiveName)
client.close()
