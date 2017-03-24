import threading as t
import json
from Threads.Ping import Ping
import struct

class HandleFromClientConnection(t.Thread):
    def __init__(self, server, socket):
        t.Thread.__init__(self)

        self.server = server
        self.socket = socket
        self.isRunning = True

        print('On a recu une connexion !')
        # Create the base Client, with just his socket and public ip.
        # self.server.addClient(socket, ip)

        # Ping(socket, self).start()

    def stop(self):
        self.isRunning = False

    def die(self):
        print('Lien rompu avec le client')
        self.stop()
        # self.server.removeClient(self.socket)

    def parseMessage(self, byteMessage):
        messageDict = json.loads(byteMessage.decode('utf-8'))
        print('Recu {}'.format(messageDict))
        action = messageDict['action']
        data = messageDict['data']

        def actionSwitch(action):
            switcher = {
                'welcome': self.server.completeClient,
                'createChannel': self.server.addChannel,
                'joinChannel': self.server.joinChannel,
                'getChannelList': self.server.getChannelList
            }
            func = switcher.get(action, lambda: "nothing")
            return func(data, self.socket)

        try:
            actionSwitch(action)
        except Exception as e:
            print(str(e))

    def recvSome(self, length):
        completeBuffer = b''
        while length:
            try:
                buffer = self.socket.recv(length)
            except Exception as e:
                self.die()
            else:
                if buffer:
                    completeBuffer += buffer
                    length -= len(buffer)
        return completeBuffer

    def run(self):
        while self.isRunning:
            binaryLength = self.recvSome(4)
            messageLength, = struct.unpack('!I', binaryLength)
            binaryMessage = self.recvSome(messageLength)

            self.parseMessage(binaryMessage)
