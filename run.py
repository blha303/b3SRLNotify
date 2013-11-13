from sys import stdout
import yaml
from twisted.internet import reactor, task, defer, protocol
from twisted.python import log
from twisted.words.protocols import irc
from twisted.application import internet, service

with open('conf/config.yml') as f:
    config = yaml.load(f.read())
HOST = config['host']
PORT = config['port'] if config['port'] else 6667
admins = config['admins']
with open('conf/games.yml') as f:
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
        if "!delgame " in message and channel == "#b3Notify":
            msg = message.replace("!delgame ", "").split(" ")
            uuser = msg[0]
            game = " ".join(msg[1:])
            if game in games:
                if uuser in games[game]:
                    games[game].remove(uuser)
                    if len(games[game]) == 0:
                        del games[game]
                    with open("conf/games.yml", "w") as file:
                        file.write(yaml.dump(games))
                    self._send_message("Done!", channel, nick=nick)
                else:
                    self._send_message("Specified user isn't in the notify list for that game :/", channel, nick=nick)
            else:
                self._send_message("Specified game has no triggers :/", channel, nick=nick)
        elif "!addgame " in message and channel == "#b3Notify":
            msg = message.replace("!addgame ", "").split(" ")
            uuser = msg[0]
            game = " ".join(msg[1:])
            if game in games:
                games[game].append(uuser)
            else:
                games[game] = [uuser]
            with open("conf/games.yml", "w") as file:
                file.write(yaml.dump(games))
            self._send_message("Done!", channel, nick=nick)
        elif "!stv " in message and channel != "#speedrunslive":
            id = message.replace("!stv ", "")
            if len(id) == 5:
                self._send_message("http://speedrun.tv/?race=" + id,
                                   channel, nick=nick)
            elif "#srl-" in message:
                self._send_message("http://speedrun.tv/?race=" +
                                   self.stv(message), channel, nick=nick)
        elif ("Race initiated for" in message or
              "Rematch initiated: " in message) and nick in ["RaceBot", "blha303"]:
            for game in games:
                if game in message:
                    for i in config["notificationchannels"]:
                        self._send_message(message + " " + self.stv(message),
                                           i, nick=", ".join(games[game]))

    def _send_message(self, msg, target, nick=None):
        if nick:
            msg = '%s, %s' % (nick, msg)
        self.msg(target, msg)

    def _show_error(self, failure):
        return failure.getErrorMessage()


class b3NotifyFactory(protocol.ReconnectingClientFactory):
    protocol = b3NotifyProtocol
    channels = config['channels']

if __name__ == '__main__':
    reactor.connectTCP(HOST, PORT, b3NotifyFactory())
    log.startLogging(stdout)
    reactor.run()
elif __name__ == '__builtin__':
    application = service.Application('b3Notify')
    ircService = internet.TCPClient(HOST, PORT, b3NotifyFactory())
    ircService.setServiceParent(application)
