import struct


class Commands:
    NULL = '\x00'
    IAC = '\xFF'

    WILL = '\xFB'
    WONT = '\xFC'
    DO = '\xFD'
    DONT = '\xFE'

    ECHO = '\x01'
    SUPPRESS_GO_AHEAD = '\x03'
    NAWS = '\x1F'

    SB = '\xFA'
    SE = '\xF0'

    ESC = '\x1B'

    CTRL_BREAK = '\x03'

    CMD_DICT = {
        IAC: 'IAC',
        WILL: 'WILL',
        WONT: 'WONT',
        DO: 'DO',
        DONT: 'DONT',
        SB: 'SB',
        SE: 'SE',
        ECHO: 'ECHO',
        SUPPRESS_GO_AHEAD: 'SUPPRESS-GO-AHEAD',
        NAWS: 'NAWS',
        CTRL_BREAK: 'CTRL_BREAK',
        NULL: 'NULL',
    }

    @classmethod
    def decode_cmd(cls, *args):
        return ' '.join(cls.CMD_DICT.get(code) for code in args)


class Utils:
    @classmethod
    def is_ascii(cls, char):
        return 32 <= ord(char) <= 126

    @classmethod
    def decode_word(cls, chars):
        return struct.unpack('>H', ''.join(chars))[0]


class ANSI:
    class Ranges:
        C0 = [(0, 0x1F)]
        SPACE = [(0x20, 0x20), (0xA0, 0xA0)]
        INTERMEDIATE = [(0x20, 0x2F)]
        PARAMETERS = [(0x30, 0x3F)]
        UPPERCASE = [(0x40, 0x5F)]
        LOWERCASE = [(0x60, 0x7E)]
        ALPHABETIC = [(0x40, 0x7E)]
        DELETE = [(0x7F, 0x7F)]
        C1 = [(0x80, 0x9F)]
        G1 = [(0xA1, 0xFE)]
        SPECIAL = [(0xA0, 0xA0), (0xFF, 0xFF)]

    KEYS = {
        '[A': 'UP',
        '[B': 'DOWN',
        '[C': 'RIGHT',
        '[D': 'LEFT',
        'OP': 'F1',
        'OQ': 'F2',
        'OR': 'F3',
        'OS': 'F4',

        'OH': 'HOME',
        'OF': 'END',

        '[1~': 'FIND',
        '[2~': 'INSERT',
        '[3~': 'DELETE',
        '[4~': 'SELECT',
        '[5~': 'PG_UP',
        '[6~': 'PG_DOWN',
        '[E~': 'KP_5',
    }

    @classmethod
    def is_in(cls, char, check_range):
        for _min, _max in check_range:
            if _min <= ord(char) <= _max:
                return True
        return False

    @classmethod
    def inspect(cls, data):
        data = ''.join(data)
        for code, value in ANSI.KEYS.items():
            if data.startswith(code):
                return len(code), value
        return 0, '?'

        # if data[0] == '[' and data[1] in 'ABCD':
        #     return dict(
        #         A=ANSI.Keys.UP,
        #         B=ANSI.Keys.DOWN,
        #         C=ANSI.Keys.RIGHT,
        #         D=ANSI.Keys.LEFT,
        #     ).get(data[1])
        # elif data[0] == 'O' and data[1] in 'OPQR':
        #     return dict(
        #         O=ANSI.Keys.F1,
        #         P=ANSI.Keys.F2,
        #         Q=ANSI.Keys.F3,
        #         R=ANSI.Keys.F4,
        #     ).get(data[1])
