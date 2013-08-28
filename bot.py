# Twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

# BeautifulSoup import
from BeautifulSoup import BeautifulSoup

# System imports
import time
import sys
from config import Config
import re
import urllib2


bot_config = {'nick':'Python',
'network':'irc.network.com',
'port':6667,
'passwd':'P@ssw0rd',
'owner':['OWNER1','OWN_2],
'db':'data.db'
}

conf_file = "bot.cfg"

exp = re.compile('(http|ftp|https):\/\/([\w\-_]+(?:(?:\.[\w\-_]+)+))([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?')

######

class bot(irc.IRCClient): 
    
    def __init__(self, config):
        self.config = Config(conf_file)
        self.channels = self.config.core.get_list('active_channels')
        self.nickname = self.config.core.nick
        self.admins = self.config.core.get_list('admins')
        self.top = self.config.core.topic
        self.stat = self.config.core.status
    
    """A basic IRC bot."""
    
    def get_url(self, str):
        m = exp.search(str)
        if m is not None:
            return str[m.start():m.end()]
        else:
            return None
            
    def get_title(self, str):       
        try:
            source = urllib2.urlopen(str)
        except urllib2.HTTPError, e:
            print "ERROR: "e.code
            return None
        else:
            headers = source.info().headers
            if not any('image' in s for s in headers):
                bs = BeautifulSoup(source)
                return bs.title.string
        
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
        url = self.get_url(msg)
        if url is not None:
            title = self.get_title(url)
            if title is not None:
                self.msg(channel, "Title: "+str(title))
        
        if len(msg.split()) > 1:
            msg = ' '.join(msg.split()[1:])
            for i in range(len(msg.split())):
                arg[i+1] = msg.split()[i]

        if cmd == self.config.core.char+'die':
            if user in bot_config['owner']:
                self.quit()
                reactor.stop()
                
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
                    self.admins.remove(args[2])
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
                
class botFactory(protocol.ClientFactory):
    global conf_file
    
    def __init__(self):
        self.config = Config(conf_file)
    
    def buildProtocol(self, addr):
        p = bot(self.config)
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        connector.connect()
    
    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()
                
if __name__ == '__main__':
    
    f = botFactory()
        
    reactor.connectTCP(bot_config['network'], bot_config['port'], f)
    
    reactor.run()
