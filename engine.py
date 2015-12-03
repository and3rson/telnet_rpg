from protocol import Commands, Utils

clients = []


class ClientHandler(object):
    @classmethod
    def create(cls, socket, address):
        client = ClientHandler(socket, address)
        client.start()

    def __init__(self, socket, address):
        self.socket = socket
        self.address = address
        self.alive = True
        self.stack = []

        print 'New connection from {}:{}'.format(*self.address)
        clients.append(self)

        self.prepare()

    def prepare(self):
        self.socket.send(Commands.IAC + Commands.WILL + Commands.ECHO)
        self.socket.send(Commands.IAC + Commands.WILL + Commands.SUPPRESS_GO_AHEAD)
        self.socket.send(Commands.IAC + Commands.WONT + Commands.EXOPL)  # TODO: Unsure about this one

        self.socket.send(Commands.ESC + '[2J')
        self.socket.send(Commands.ESC + '[0;0H')

        self.socket.send('Hello!\r\n')

    def start(self):
        while self.alive:
            data = self.socket.recv(1)
            if not data:
                print 'Connection {}:{} dropped'.format(*self.address)
                clients.remove(self)
                self.alive = False
            else:
                print 'Got data:', repr(data)
            self.stack.append(data)

            self.process()

    def process(self):
        if not len(self.stack):
            return

        head = self.stack[0]
        if head == Commands.IAC:
            if len(self.stack) >= 3:
                self.stack.pop(0)
                print 'Got command:', Commands.decode_cmd(self.stack.pop(0) + self.stack.pop(0))
            return

        elif Utils.is_ascii(head):
            self.stack.pop(0)
            self.socket.send(head)
        elif head == '\x0D':
            self.stack.pop(0)
            self.socket.send('\x0D\x0A')

        else:
            print 'Unexpected byte - {}'.format(repr(head))
            self.stack.pop(0)

            # ANSI escape codes: http://www.tldp.org/HOWTO/Bash-Prompt-HOWTO/x361.html
            # self.socket.send(Commands.ESC + '[1B')
