class Commands:
    IAC = '\xFF'

    WILL = '\xFB'
    WONT = '\xFC'
    DO = '\xFD'
    DONT = '\xFE'

    ECHO = '\x01'
    SUPPRESS_GO_AHEAD = '\x03'
    EXOPL = '\xFF'

    ESC = '\x1B'

    CMD_TYPE = {
        WILL: 'WILL',
        WONT: 'WONT',
        DO: 'DO',
        DONT: 'DONT'
    }

    CMD_NAME = {
        ECHO: 'ECHO',
        SUPPRESS_GO_AHEAD: 'SUPPRESS-GO-AHEAD',
        EXOPL: 'EXOPL'
    }

    @classmethod
    def decode_cmd(cls, cmd):
        return u'{} {}'.format(
            cls.CMD_TYPE.get(cmd[0], '???'),
            cls.CMD_NAME.get(cmd[1], '???')
        )


class Utils:
    @classmethod
    def is_ascii(cls, char):
        return 32 <= ord(char) <= 126
