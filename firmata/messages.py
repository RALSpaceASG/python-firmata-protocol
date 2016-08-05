from constants import (
    DIGITAL_MESSAGE, ANALOG_MESSAGE, PROTOCOL_VERSION
)


class DigitalData(object):

    def __init__(self, data):
        assert (data[0] & 0xF0) == DIGITAL_MESSAGE
        self.port = data[0] & 0x0F
        self.value = (data[2] << 7) + data[1]

    def __repr__(self):
        return "<DigitalData port:{:d}, value:0b{:08b}>".format(
            self.port, self.value)


class AnalogData(object):

    def __init__(self, data):
        assert (data[0] & 0xF0) == ANALOG_MESSAGE
        self.pin = data[0] & 0x0F
        self.value = (data[2] << 7) + data[1]

    def __repr__(self):
        return "<AnalogData pin:{:d}, value:{:d}>".format(
            self.pin, self.value)


class ProtocolVersion(object):

    def __init__(self, data):
        assert data[0] == PROTOCOL_VERSION

        self.major = data[1]
        self.minor = data[2]

    def __repr__(self):
        return "<ProtocolVersion version:{:d}.{:d}>".format(
            self.major, self.minor)
