"""
firmata
~~~~~~~

A library for communicating with the firmata protocol.

Based on the principle in Cory Benfield's talk at PyCon 2016,
"Building Protocol Libraries The Right Way":https://youtu.be/7cC3_jGwl_U
"""

from constants import (
    START_SYSEX, END_SYSEX,
    DIGITAL_MESSAGE, ANALOG_MESSAGE, PROTOCOL_VERSION
)
from sysex import SysExMessage


class ProtocolError(Exception):
    pass


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


class FirmataPacketBuffer(object):
    """
    This is a data structure that expects to act as a buffer for Firmata data
    that allows iteration in terms of Firmata packets
    """
    def __init__(self):
        self.data = bytearray()

    def add_data(self, data):
        """
        Add more data to the packet buffer.
        :param data: A bytestring containing the byte buffer.
        """

        self.data += data

    def _read_data(self, amt):
        if len(self.data) < amt:
            raise StopIteration

        _data = self.data[:amt]
        self.data = self.data[amt:]

        return _data

    def __iter__(self):
        return self

    def __next__(self):
        # frame MIDI packets
        # midi packets are command or data,
        # based on the most-significant bit
        # command words can be followed
        # by up to two data words, unless
        # it is a SysEx command

        if not self.data:
            raise StopIteration

        # check that we have a proper start to the packet
        if not self.data[0] & 0x80:
            raise ProtocolError("Packet must begin with a command byte")

        # handle based on next command byte
        if (self.data[0] & 0xF0) == DIGITAL_MESSAGE:
            packet = DigitalData(self._read_data(3))
        elif (self.data[0] & 0xF0) == ANALOG_MESSAGE:
            packet = AnalogData(self._read_data(3))
        elif self.data[0] == START_SYSEX:
            if END_SYSEX not in self.data:
                raise StopIteration
            packet, stop, self.data = self.data.partition(b'\xf7')
            packet = SysExMessage(packet + stop)
        elif self.data[0] == PROTOCOL_VERSION:
            packet = ProtocolVersion(self._read_data(3))
        else:
            raise ProtocolError("Unrecognized command byte")

        return packet

    def next(self):  # Python 2
        return self.__next__()


class FirmataConnection(object):

    def __init__(self):

        self._data_to_send = bytearray()

    def data_to_send(self, amt=None):
        """
        Returns some data for sending out of the internal data buffer.

        This method is analagous to ``read`` on a file-like object, but it
        doesn't block. Instead, it returns as much data as the user asks for,
        or less if that much data is not available. It does not perform any
        I/O, and so uses a different name.

        :param amt: (optional) The maximum amount of data to return. If not
            set, or set to ``None``, will return as much data as possible.
        :type amt: ``int``
        :returns: A bytestring containing the data to send on the wire.
        :rtype: ``bytes``
        """
        if amt is None:
            data = self._data_to_send
            self._data_to_send = bytearray()
            return data
        else:
            data = self._data_to_send[:amt]
            self._data_to_send = self._data_to_send[amt:]
            return data

    def receive_data():
        pass

    def initiate_connection():
        pass
