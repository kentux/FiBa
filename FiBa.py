#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, ConfigParser, tarfile, socket, time, scp, paramiko, smtplib, sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from docopt import docopt

help = """ FiBa

Usage:
    FiBa.py FILE

Arguments:
    FILE                    Fichier de configuration (Obligatoire)

Options:
    -h --help               Généré automatiquement

"""

arguments = docopt(help)

config = ConfigParser.ConfigParser()
config.read(arguments['FILE'])

dirs_files = []

for s in config.sections():
    if s == 'Server':
        serverName = config.get(s, 'Name')
        serverUrl = config.get(s, 'Url')
        serverPort = int(config.get(s, 'Port'))
        serverUser = config.get(s, 'User')
        serverKey = paramiko.RSAKey.from_private_key_file(config.get(s, 'Key'))
    elif s == 'Email':
        sender = config.get(s, 'Sender')
        receiver = config.get(s, 'Receiver')
    elif s == 'Archive':
        archiveName = '/tmp/' + config.get(s, 'Name') + '_' + socket.gethostname().split('.')[0] + '_' + time.strftime("%Y%m%d%H%M%S") + '.tar.gz'
    else:
        infoName = s
        path = config.get(s, 'Path').split()
        dirs_files.append( (infoName, path, ) )


tar = tarfile.open(archiveName, "w:gz")

for infoName, fileList in dirs_files:
    for f in fileList:
        tar.add(f)

tar.close()

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname = serverUrl, port = serverPort, username = serverUser, pkey = serverKey)
trans = scp.SCPClient(client.get_transport())
trans.put(archiveName)
client.close()

msg = MIMEMultipart('alternative')
msg['Subject'] = "Backup " + archiveName + " terminé !"
msg['From'] = sender
msg['To'] = receiver

text = "Hi!\n Backup terminé."
html = """\
<html>
    <head></head>
    <body>
        <h1>Hi!</h1>
        <h3>Backup terminé.</h3>
    </body>
</html>"""

part1 = MIMEText(text, 'plain')
part2 = MIMEText(html, 'html')

msg.attach(part1)
msg.attach(part2)

s = smtplib.SMTP('localhost')
s.sendmail(sender, receiver, msg.as_string())
s.quit()
