"""
sysex.py
~~~~~~~~

Event objects and other classes for dealing with
Firmata SysEx messages in firmata-protocol module.
"""

from constants import (
    START_SYSEX, END_SYSEX,
    STRING_DATA, REPORT_FIRMWARE,
    PIN_STATE_QUERY, PIN_STATE_RESPONSE
)


def _bytes_representation(data):
    return "".join("\\x{:02x}".format(c) for c in data)


class SysExMessage(object):

    def __init__(self, data):
        assert data[0] == START_SYSEX
        assert data[-1] == END_SYSEX

        self.command = data[1]
        self.data = data[2:-1]

    def __repr__(self):
        return "<SysExMessage command:{}, data:{}>".format(
            _bytes_representation([self.command]),
            _bytes_representation(self.data)
        )


class StringData(object):
    def __init__(self, sysex):
        assert sysex.command == STRING_DATA

        # convert data to string
        # group into tuples of (MSB, LSB)
        pairs = zip(sysex.data[1::2], sysex.data[::2])
        string = bytearray((msb << 7) + lsb for msb, lsb in pairs)
        # is it a good idea to decode?
        self.string = string.decode('ascii')

    def __str__(self):
        return self.string

    def __repr__(self):
        return "<StringData string:'{}'>".format(self.string)


class ReportFirmware(object):
    def __init__(self, sysex):
        assert sysex.command == REPORT_FIRMWARE

        self.major = sysex.data[0]
        self.minor = sysex.data[1]

        # get firmware names
        self.name = bytearray(
            (msb << 7) + lsb for msb, lsb in zip(sysex.data[3::2],
                                                 sysex.data[2::2])
            ).decode('ascii')

    def __repr__(self):
        return "<ReportFirmware version:{}.{}, name:'{}'>".format(
            self.major, self.minor, self.name
        )


class PinStateResponse(object):
    def __init__(self, sysex):
        assert sysex.command == PIN_STATE_RESPONSE

        self.pin = sysex.data[0]
        self.pin_mode = sysex.data[1]

        self.pin_state = 0
        for i, bits in enumerate(sysex.data[2:]):
            self.pin_state += (bits & 0x7F) << i*7

    def __repr__(self):
        return "<PinStateResponse pin:{}, pin_mode:{}, pin_state:{}>".format(
            self.pin, self.pin_mode, self.pin_state
        )


class SysExRegistry(object):
    """
    A factory class for converting generic SysExMessage events
    to specific events for Firmata message types.

    Should help with ConfigurableFirmata by having the ability
    to add and remove event types as desired.
    """

    # map of command bytes to event object constructors
    # start with the built-in Firmata types
    # we only include the ones that can be received
    _firmata_sysex = {
        # 0x60: SerialMessage,
        # 0x61: EncoderData,
        # 0x6A: AnalogMappingResponse,
        # 0x6C: CapabilityResponse,
        # 0x6E: PinStateResponse,
        STRING_DATA: StringData,
        # 0x77: I2CReply,
        REPORT_FIRMWARE: ReportFirmware
    }

    def __init__(self):
        self._sysex_types = self._firmata_sysex

    def from_sysex(self, sysex):
        try:
            sysex = self._sysex_types[sysex.command](sysex)
        except KeyError:
            # if we have no handler for the specific
            # sysex, just return the original
            pass
        return sysex


class SysEx(object):

    def send_query_firmware(self):
        message = bytearray([START_SYSEX, REPORT_FIRMWARE, END_SYSEX])
        super()._prepare_for_sending(message)

    def send_pin_state_query(self, pin):
        message = bytearray([START_SYSEX, PIN_STATE_QUERY, pin, END_SYSEX])
        super()._prepare_for_sending(message)
