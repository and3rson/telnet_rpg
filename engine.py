from protocol import Commands, Utils, ANSI
import traceback

clients = []


class ClientHandler(object):
    class State(object):
        IDLE = 0
        EXPECT_COMMAND = 1
        SUBNEGOTIATION = 3

    @classmethod
    def create(cls, socket, address):
        client = ClientHandler(socket, address)
        client.start()

    def __init__(self, socket, address):
        self.socket = socket
        self.address = address
        self.alive = True
        self.stack = []
        self.state = ClientHandler.State.IDLE

        self.cmd = None
        self.args = None

        print 'New connection from {}:{}'.format(*self.address)
        clients.append(self)

        self.prepare()

    def prepare(self):
        self.socket.send(Commands.IAC + Commands.WILL + Commands.ECHO)
        self.socket.send(Commands.IAC + Commands.WILL + Commands.SUPPRESS_GO_AHEAD)
        # self.socket.send(Commands.IAC + Commands.WONT + Commands.EXOPL)  # TODO: Unsure about this one

        self.socket.send(Commands.IAC + Commands.DO + Commands.NAWS)

        self.socket.send(Commands.ESC + '[2J')
        self.socket.send(Commands.ESC + '[0;0H')

        self.socket.send('Hello!\r\n')

    def start(self):
        while self.alive:
            data = self.socket.recv(1024)
            if not data:
                print 'Connection {}:{} dropped'.format(*self.address)
                clients.remove(self)
                self.alive = False
            else:
                print 'Got data:', repr(data)
            self.stack.extend(data)

            self.process()

    def process(self):
        while len(self.stack):
            head = self.stack[0]
            if head == Commands.IAC and len(self.stack) >= 2:
                op = self.stack[1]

                if len(self.stack) >= 3:
                    iac = self.stack.pop(0)
                    op = self.stack.pop(0)
                    action = self.stack.pop(0)
                    print 'Got command:', Commands.decode_cmd(iac, op, action)

                    if op == Commands.SB:
                        data = []
                        while self.stack[0:2] != [Commands.IAC, Commands.SE]:
                            b = self.stack.pop(0)
                            data.append(b)
                        self.stack.pop(0)
                        self.stack.pop(0)

                        print 'Subnegotiation data:', [ord(x) for x in data]

                        self.handle_command(op, action, data)

                    continue
                # elif op == Commands.SB and (Commands.IAC + Commands.SE in ''.join(self.stack)):
                #     iac = self.stack.pop(0)
                #     op = self.stack.pop(0)
                #     action = self.stack.pop(0)
                #
                #
                #     continue
                else:
                    return

            elif Utils.is_ascii(head):
                self.stack.pop(0)
                self.socket.send(head)

                continue

            elif head == '\x0D':
                self.stack.pop(0)
                self.socket.send('\x0D\x0A')

            elif head == '\t':
                self.stack.pop(0)
                self.socket.send('<TAB>')

                continue
            elif head == Commands.ESC:
                # if len(self.stack) >= 2:
                #     self.socket.send(self.stack)
                # else:

                self.stack.pop(0)

                # TODO: Implement escape char parsing
                code_len, value = ANSI.inspect(self.stack)
                self.socket.send('<{}>'.format(value))

                for i in xrange(code_len):
                    self.stack.pop(0)

                    # self.socket.send('<ESCAPE>')

                continue

            elif head == Commands.CTRL_BREAK:
                self.stack.pop(0)
                self.socket.send('<CTRL+C>')

                continue

            elif head == '\x7F':
                self.stack.pop(0)
                self.socket.send('<BACKSPACE>')

                continue

            elif head == Commands.NULL:
                self.stack.pop(0)

            else:
                print 'Unexpected byte - {}'.format(repr(head))
                b = self.stack.pop(0)

                self.socket.send('<0x{}>'.format('%02X' % ord(b)))

                return

                # ANSI escape codes: http://www.tldp.org/HOWTO/Bash-Prompt-HOWTO/x361.html
                # self.socket.send(Commands.ESC + '[1B')

    def handle_command(self, op, action, data):
        if op == Commands.SB and action == Commands.NAWS:
            try:
                print '* Client screen size: {}x{}'.format(
                    Utils.decode_word(data[0:2]),
                    Utils.decode_word(data[2:4]),
                )
            except:
                exc = traceback.format_exc()
                print exc
                self.socket.send(exc)
