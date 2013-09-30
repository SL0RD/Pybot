# Twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log


# BeautifulSoup import
from BeautifulSoup import BeautifulSoup

# Bot imports
import url
from config import Config
from calc import calc

# System imports
import time
import sys
import re
import urllib2

conf_file = "bot.cfg"
version = '0.3'
network = 'irc.nuxxor.com'
port = 6667
exp = re.compile('(http|ftp|https):\/\/([\w\-_]+(?:(?:\.[\w\-_]+)+))([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?')

######

class bot(irc.IRCClient): 
    
    def __init__(self, config):
        self.url = url
        self.config = Config(conf_file)
        self.channels = self.config.core.get_list('active_channels')
        self.network = self.config.core.network
        self.port = self.config.core.port
        self.nickname = self.config.core.nick
        self.admins = self.config.core.get_list('admins')
        self.owner = self.config.core.owner
        self.top = self.config.core.topic
        self.stat = self.config.core.status
        self.starttime = time.time()
        self.version = version
	self.calc = calc
     ##   self.twchan = "#besttechie"
    
    """A basic IRC bot."""
                
    def get_uptime(self):
        curtime = time.time()
        uptime = curtime - self.starttime
        week = int(uptime / 604800)
        uptime = uptime - week * 604800
        day = int(uptime / 86400)
        uptime = uptime - day * 86400
        hour = int(uptime / 3600)
        uptime = uptime - hour * 3600
        minute = int(uptime / 60)
        uptime = uptime - minute * 60
        second = int(uptime)
        return "I have been running for: "+str(week)+" week(s) "+str(day)+" day(s) "+str(hour)+" hour(s) "+str(minute)+" minute(s) "+str(second)+" second(s)"
        
    def noticed(self, user, chan, msg):
        user = user.split('!', 1)[0]
        if user == "NickServ" and "This nickname is registered" in msg:
            msg = "identify "+self.config.core.passwd
            print "Identifying..."
            self.msg(user, msg)
        if user == "NickServ":
            if "now identified" in msg or "Password accepted" in msg:
                print "Identified to nickserv"

    def userJoined(self, user, chan):
        user = user.split('!', 1)[0]
        if user not in self.admins:
            self.mode(chan, True, '+v', None, user, None)
            
    def signedOn(self):
        for chan in self.channels:
            self.join(chan)

    def joined(self, channel):
        if channel not in self.channels:
            self.channels.append(channel)
            self.config.parser.set('core','active_channels',','.join(self.channels))
            self.config.save()
        
    def left(self, channel):
        if channel in self.channels:
            self.channels.remove(channel)
            self.config.parser.set('core','active_channels',','.join(self.channels))
            self.config.save()
        
    def privmsg(self, user, channel, msg):
        chan = channel[1:]
        user = user.split('!', 1)[0]
        cmd = msg.split(' ', 1)[0]
        arg = {}
        url = self.url.get_url(msg)
        
        if url is not None:
            title = self.url.get_title(url)
            if title is not None:
                self.msg(channel, "Title: "+str(title))
        
        if len(msg.split()) > 1:
            msg = ' '.join(msg.split()[1:])
            for i in range(len(msg.split())):
                arg[i+1] = msg.split()[i]
        
        if cmd == self.config.core.char+'version':
            self.msg(channel, "I'm currently running version "+str(version))

        if cmd == self.config.core.char+'die':
            if user in self.owner:
                self.quit()
                reactor.stop()
               ## twitss.threading.Timer.cancel()
                
        if cmd == self.config.core.char+'join':
            if user in self.admins:
                if arg[1] not in self.channels:
                    self.join(arg[1])
                else:
                    self.msg(channel, "I'm already in that channel")
                
        if cmd == self.config.core.char+'part':
            if user in self.admins:
                if arg[1] in self.channels:
                    self.leave(arg[1])
                else:
                    self.msg(channel,"I'm not in that channel")
        
        if cmd == self.config.core.char+'channels':
            self.msg(channel, "Current channels: "+', '.join(self.channels))
        
        if cmd == self.config.core.char+'admin':
            if arg[1] == 'add':
                if arg[2] not in self.admins:
                    self.admins.append(arg[2])
                    self.config.parser.set('core','admins',','.join(self.admins))
                    self.config.save()
                    print "Added "+arg[2]+" to the admin list"
            
            elif arg[1] == 'del':
                if arg[2] in self.admins:
                    self.admins.remove(arg[2])
                    self.config.parser.set('core','admins',','.join(self.admins))
                    self.config.save()
                    print "Removed "+arg[2]+" from the admin list"
            
            elif arg[1] == 'list':
                self.msg(channel, "Current admins: "+', '.join(self.admins))
                
        if cmd == self.config.core.char+'topic':
            if user in self.admins:
                self.top = msg
                self.config.parser.set('core','topic',self.top)
                self.topic(channel, self.top+' || '+self.stat)
                self.config.save()
                
        if cmd == self.config.core.char+'status':
            if user in self.admins:
                self.stat = msg
                self.config.parser.set('core','status',self.stat)
                self.topic(channel, self.top+' || '+self.stat)
                self.config.save()
                
        if cmd == self.config.core.char+'uptime':
            self.msg(channel, str(self.get_uptime()))

        if cmd == self.config.core.char+'calc':
            self.msg(channel, str(self.calc(msg)))

                
class botFactory(protocol.ClientFactory):
    global conf_file
    
    def __init__(self):
        self.config = Config(conf_file)
    
    def buildProtocol(self, addr):
        p = bot(self.config)
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        print "Connection lost. Reconnecting..."
        connector.connect()
    
    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()
                
if __name__ == '__main__':
    
    print "Starting Pybot Version: "+str(version)
    f = botFactory()
        
    reactor.connectTCP(network, port, f)
    
    print "Connecting..."
    
    reactor.run()
