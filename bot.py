import sys
import socket
import time

bnick = 'BOT_NICK'
debug = True
network = 'NETWORK'
port = 6667
bpass = 'PASSWORD'
admins = ['ADMIN','ADMIN_2']
trigchar = '.'
owner = ['OWNER','OTHEROWNER']

if debug == True:
	chan = '#dev-channel'
elif debug == False:
	chan = '#main-channel'


def get_nick(hln):
	data = hln.split() [0]
	return data[(data.find(":")+1):(data.find("!"))]
	
def isop(nick):
	if nick in admins:
		return 1
	else: 
		return 0
		
def get_chan(str):
	return str[(str.find("#")):].split() [0]

def isown(nick):
	if nick in owner:
		return 1
	else:
		return 0
	
def get_args(arg, cmd):
	return arg[(arg.find(cmd)) +len(cmd)+1:]

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc.connect((network, port))

print irc.recv (4096)

irc.send('NICK ' + bnick + '\r\n')
irc.send('USER '+ bnick + ' 0 * :' + bnick + '\r\n')

while True:

	data = irc.recv ( 4096 )
	print data

	if data.find ( 'PING' ) != -1:
		irc.send ( 'PONG ' + data.split() [ 1 ] + '\r\n' )

	elif data.find (trigchar + 'die') != -1:
		if isop(get_nick(data)) == 1:
			irc.send ( 'PRIVMSG '+get_chan(data)+' :Shutting down...\r\n' )
			irc.send ( 'QUIT :Disconnecting...\r\n')
			break
		else:
			irc.send ( 'PRIVMSG #bots : You are not an Op.\r\n' )

	elif data.find ( 'JOIN :#' ) != -1:
		if get_nick(data) != bnick:
			if isop(get_nick(data)) == 0:
				irc.send ( 'MODE #bots +v ' + get_nick(data) + '\r\n' )
			else:
				irc.send ( 'PRIVMSG #bots :Shhh! Its an admin.... :P\r\n' )

	elif data.find (trigchar + 'topic') != -1:
		if get_nick(data) != bnick:
			if isop(get_nick(data)) == 1:
				top = get_args(data, trigchar+'topic')
				irc.send ('TOPIC ' + chan + ' :' + top + '\r\n')

	elif data.find (trigchar+'join') != -1:
		if get_nick(data) !=bnick:
			if isown(get_nick(data)) == 1:
				chan = get_args(data, trigchar+'join')
				irc.send ('JOIN '+chan+'\r\n')

	elif data.find (trigchar+'part') != -1:
		if get_nick(data) != bnick:
			if isown(get_nick(data)) == 1:
				if  len(get_args(data, trigchar+'part'))  > 1:
					chan = get_args(data, trigchar+'part')
					irc.send ('PART '+chan+'\r\n')
				else:
					irc.send ('PART '+get_chan(data)+'\r\n')
				
	elif data.find ('This nickname is registered') != -1:
		if get_nick(data) != bnick:
			if get_nick(data) == 'NickServ':
				irc.send ('PRIVMSG NickServ :identify '+bpass+'\r\n')

	elif data.find ('Password accepted - you are now recognized') != -1:
		irc.send ('JOIN ' + chan + '\r\n')
