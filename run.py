from sys import stdout
import yaml
from twisted.internet import reactor, task, defer, protocol
from twisted.python import log
from twisted.words.protocols import irc
from twisted.web.client import getPage
from twisted.application import internet, service

with open('config.yml') as f:
    config = yaml.load(f.read())
HOST = config['host']
PORT = config['port'] if config['port'] else 6667
admins = config['admins']
with open('games.yml') as f:
    games = yaml.load(f.read())

class b3NotifyProtocol(irc.IRCClient):
    nickname = config['nick']
    username = config['user']
    versionName = config['version'][0]
    versionNum = config['version'][1]
    realname = config['real']
    sourceURL = config['source']
    fingerReply = config['finger']
 
    def signedOn(self):
        for channel in self.factory.channels:
            self.join(channel)
 
    def stv(self, message):
        split = message.split(" ")
        id = None
        for i in split:
            if "#srl-" in i:
                id = i[5:]
        if id:
            return "http://speedrun.tv/?race=" + id
        else:
            return ""

    def privmsg(self, user, channel, message):
        nick, _, host = user.partition('!')
        message = message
        if "!stv " in message:
            id = message.replace("!stv ", "")
            if len(id) == 5:
                self._send_message("http://speedrun.tv/?race=" + id, channel, nick=nick)
            elif "#srl-" in message:
                self._send_message("http://speedrun.tv/?race=" + self.stv(message), channel, nick=nick)
        elif ("Race initiated for" in message or "Rematch initiated: " in message) and nick in ["RaceBot", "blha303"]:
            for game in games:
                if game in message:
                    for name in games[game]:
                        self._send_message(message + " " + self.stv(message), name)
 
    def _send_message(self, msg, target, nick=None):
        if nick:
            msg = '%s, %s' % (nick, msg)
        self.msg(target, msg)
 
    def _show_error(self, failure):
        return failure.getErrorMessage()
 
class b3NotifyFactory(protocol.ReconnectingClientFactory):
    protocol = b3NotifyProtocol
    channels = ['#b3Notify', '#speedrunslive']
 
if __name__ == '__main__':
    reactor.connectTCP(HOST, PORT, b3NotifyFactory())
    log.startLogging(stdout)
    reactor.run()
 
elif __name__ == '__builtin__':
    application = service.Application('b3Notify')
    ircService = internet.TCPClient(HOST, PORT, b3NotifyFactory())
    ircService.setServiceParent(application)
