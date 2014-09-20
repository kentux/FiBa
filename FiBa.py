#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, ConfigParser, tarfile, socket, time, paramiko

config = ConfigParser.ConfigParser()
config.read("FiBa.conf")


dirs_files = []

for s in config.sections():
    if s == 'Server':
        serverName = config.get(s, 'Name')
        serverUrl = config.get(s, 'Url')
        serverPort = config.get(s, 'Port')
        serverUser = config.get(s, 'User')
        serverKey = config.get(s, 'Key')
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

paramiko.util.log_to_file('/tmp/paramiko.log')
k = paramiko.RSAKey.from_private_key_file(serverKey)
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#c.connect( hostname = serverUrl, username = serverUser, pkey = k )
c = paramiko.Transport(( serverUrl, int(serverPort) ))
c.connect( username = serverUser, pkey = k )
trans = paramiko.SFTPClient.from_transport(c)
sftp.put(archiveName)
c.close()
