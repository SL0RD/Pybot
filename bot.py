import sys
import socket
import time

bnick = 'Python'
debug = True
network = 'irc.nuxxor.com'
port = 6667
admins = ['SL0RD','SL0RD|MBP']
trigchar = '.'
owner = ['SL0RD','SL0RD|MBP']

if debug == True:
	chan = '#bots'
elif debug == False:
	chan = '#bikdip'


def get_nick(hln):
	data = hln.split() [0]
	return data[(data.find(":")+1):(data.find("!"))]
	
def isop(nick):
	if nick in admins:
		return 1
	else: 
		return 0

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
irc.send('USER Python 0 * :Python\r\n')

while True:
	data = irc.recv ( 4096 )
	print data
	if data.find ( 'PING' ) != -1:
		irc.send ( 'PONG ' + data.split() [ 1 ] + '\r\n' )
	elif data.find ( '!die' ) != -1:
		if isop(get_nick(data)) == 1:
			irc.send ( 'PRIVMSG #bots :Shutting down...\r\n' )
			irc.send ( 'QUIT :Disconnecting...\r\n')
			irc.close()
		else:
			irc.send ( 'PRIVMSG #bots : You are not an Op.\r\n' )
	elif data.find ( 'JOIN :#' ) != -1:
		if get_nick(data) != bnick:
			if isop(get_nick(data)) == 0:
				irc.send ( 'PRIVMSG #bots :Welcome ' + get_nick(data) + '\r\n' )
			else:
				irc.send ( 'PRIVMSG #bots :Shhh! Its an admin.... :P\r\n' )
	elif data.find (trigchar + 'topic') != -1:
		if get_nick(data) != bnick:
			if isop(get_nick(data)) == 1:
				top = get_args(data, trigchar+'topic')
				irc.send ('TOPIC ' + chan + ' :' + top + '\r\n')
				#irc.send ('PRIVMSG ' + chan + ' :' + top + '\r\n')
	elif data.find (trigchar+'join') != -1:
		if get_nick(data) !=bnick:
			if isown(get_nick(data)) == 1:
				chan = get_args(data, trigchar+'join')
				irc.send ('JOIN '+chan+'\r\n')
	elif data.find (trigchar+'part') != -1:
		if get_nick(data) != bnick:
			if isown(get_nick(data)) == 1:
				chan = get_args(data, trigchar+'part')
				irc.send ('PART '+chan+'\r\n')
	elif data.find ('Welcome') != -1:
		time.sleep(2)
		irc.send ('JOIN ' + chan + '\r\n')
	
