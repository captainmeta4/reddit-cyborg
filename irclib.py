import socket
import re

'''
A custom IRC handler/wrapper for bots by captainmeta4
'''

class IRC():

    def __init__(self):
        self.servers = []

    def add_server(self, host, port, nick, ident, password, realname, channels=[],raw=False):

        self.servers.append(Server(host, port, nick, ident, password, realname, channels, raw))


    def listen(self):

        for server in self.servers:
            server.s.setblocking(0)

        while True:
            for server in self.servers:
                for line in server.listen_line():
                    try:
                        yield Message(server, line)
                    except:
                        continue
                

    

class Server():

    def __init__(self, host, port, nick, ident, password, realname, channels=[],raw=False):

        self.host=host
        self.port=int(port)
        self.nick=nick
        self.ident=ident
        self.password=password
        self.realname=realname
        self.raw=raw
        self.readbuffer=""

        self.connect()
        self.auth()
        
        self.channels = []
        for name in channels:
            self.add_channel(name)

    def add_channel(self, name):
        x = Channel(self, name)
        x.join()
        if x not in self.channels:            
            self.channels.append(x)

    def part_channel(self, name):

        for channel in self.channels:
            if channel.name.lower() == name.lower():
                channel.part()
        
    def connect(self):
        self.s=socket.socket()
        try:
            print('attempting to connect to {0}:{1}...'.format(self.host,str(self.port)))
            self.s.connect((self.host,self.port))
            print('...success')
        except TimeoutError:
            print('Timed out. Trying again')
            self.connect()

    def auth(self):
        self.send("PASS %s" % self.password)
        self.send("NICK %s" % self.nick)
        self.send("USER %s %s bla :%s" % (self.ident, self.host, self.realname))
        self.wait_for("Password accepted")

    def send(self, text):
        x= self.s.send(bytes(text+"\r\n", "UTF-8"))
        print('sent to '+self.host+': '+text)

    def notice(self, target, text):
        lines = text.split('\n\n')
        for line in lines:
            self.send("NOTICE {0} :{1}".format(target, text))
            
    def speak(self, target, text):
        lines = text.split('\n\n')
        for line in lines:
            self.send("PRIVMSG {0} :{1}".format(target, text))

    def wait_for(self, text,):

        if isinstance(text, str):
            text = [text]

        self.s.setblocking(1)
        
        for line in self.listen_raw():
            if any(x in line for x in text):
                self.s.setblocking(0)
                return line

            
    def listen_raw(self):
        readbuffer=""
        while True:
            readbuffer=readbuffer+str(self.s.recv(1024), "UTF-8", errors='replace')
            temp=readbuffer.split("\r\n")
            readbuffer=temp.pop()

            for line in temp:
                
                linelist=line.split()
                if(linelist[0]=="PING"):
                    print(line)
                    self.send("PONG {}".format(linelist[1]))
                    continue
                
                line=line.rstrip()
                print(line)
                yield line

    def listen_line(self):
        try:
            self.readbuffer=self.readbuffer+str(self.s.recv(1024), "UTF-8", errors='replace')
        except BlockingIOError:
            return
        temp=self.readbuffer.split("\r\n")
        self.readbuffer=temp.pop()

        for line in temp:

            #handle pings
            linelist=line.split()       
            if(linelist[0]=="PING"):
                print(line)
                self.send("PONG %s" % linelist[1])
                continue
                
            line=line.rstrip()
            print(line)
            yield line


    def speak(self, target, text):

        self.send("PRIVMSG {0} :{1}".format(target, text))

class Channel():

    def __init__(self, server, name):

        self.server = server
        self.name = name

        if not self.name.startswith("#"):
            raise ValueError("Channel name must start with '#'")

        self.joined = False
    

    def join(self):
        self.server.send("JOIN "+self.name)

    def part(self):
        self.server.send("PART "+self.name)

    def talk(self, text):
        self.server.send("PRIVMSG {0} :{1}".format(self.name, text))

class User():

    def __init__(self, server, nick):
        self.nick = nick
        self.server = server

        #given the nick, find out more about the user
        self.server.send("WHOIS {}".format(self.nick))
        response = self.server.wait_for([" 311 "+self.server.nick," 401 "+self.server.nick])
        if "401" in response:
            raise ValueError("No such nick")
        
        #regex for info
        s=":\S+ 311 {} {} (\S+) (\S+) \* :(.+)$".format(self.server.nick, self.nick)
        x=re.search(s, response, flags=re.IGNORECASE)
        
        self.userid=x.group(1)
        self.host=x.group(2)
        self.realname = x.group(3)

        self.mask = self.userid+"@"+self.host
        
    def msg(self, text):
        self.server.speak(self.nick, text)
            

class Message():

    def __init__(self, server, raw):

        self.server=server
        self.raw = raw

        #regex the raw to extract the message properties
        # https://regex101.com/r/GHg2Ul/2
        x = re.search("^:((\S+?)!)?((\S+?)@)?(\S+?) ([A-Z]+?) (\S+?)?( \S+?)? ?:(.*)$",raw)
        self.nick = x.group(2)
        self.userid = x.group(4)
        self.host=x.group(5)
        self.type=x.group(6)
        self.target=x.group(7)
        self.secondary_target=x.group(8)
        self.body = x.group(9)


    def __str__(self):
        if self.server.raw:
            return(self.raw)
        else:
            output = "{0} / {1} / {2} / {3}".format(self.server.host,self.channel,self.nick,self.body)
            return output

    def reply(self, text):
        if self.target.startswith("#"):
            self.server.speak(self.target, text)
        elif self.target==self.server.nick:
            self.server.speak(self.nick, text)

