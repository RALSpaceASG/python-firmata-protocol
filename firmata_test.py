#!/usr/bin/env python3
"""
firmata_test.py
~~~~~~~~~~~~~~~

Unit tests for firmata.py.
"""
import unittest

import firmata
import sysex


class FirmataTest(unittest.TestCase):

    # port 9 bitmask 0b10110110
    digital_data = bytearray([0x99, 0b00110110, 0b00000001])
    # analog pin 9 14-bit value 3456
    analog_data = bytearray([0xE9, 0x00, 0b11011])
    string_data = bytearray([0xF0, 0x71, 0x54, 0x00, 0xF7])

    def setUp(self):
        self.digital_event = firmata.DigitalData(self.digital_data)
        self.analog_event = firmata.AnalogData(self.analog_data)
        self.sysex_message = firmata.SysExMessage(self.string_data)
        self.string_sysex = sysex.StringData(self.sysex_message)

        self.connection = firmata.FirmataConnection()

    def assertEventEqual(self, eventA, eventB):
        '''test if two events are equilavent'''
        # assume that if the representations match, that is sufficient
        self.assertEqual(eventA.__repr__(), eventB.__repr__())


class FirmataPacketBufferTest(FirmataTest):

    def setUp(self):
        super(FirmataPacketBufferTest, self).setUp()
        self.packet_buffer = firmata.FirmataPacketBuffer()

        self.datas = map(bytes, (
            self.digital_data, self.analog_data, self.string_data))
        self.events = map(bytes, (
            self.digital_event, self.analog_event, self.sysex_message))

    def assertNextEventEqual(self, event):
        self.assertEventEqual(self.packet_buffer.__next__(), event)

    def assertEmpty(self):
        self.assertRaises(StopIteration, self.packet_buffer.__next__)

    def add_all(self):
        for data in self.datas:
            self.packet_buffer.add_data(data)

    def test_empty(self):
        self.assertEmpty()

    def test_iter_empty(self):
        packets = list(self.packet_buffer)
        self.assertEqual(packets, [])

    def test_all(self):
        self.add_all()

        events = (self.digital_event, self.analog_event, self.sysex_message)

        for packet, event in zip(self.packet_buffer, events):
            self.assertEventEqual(packet, event)

    def test_partial_single(self):
        # leave off last byte
        self.packet_buffer.add_data(self.digital_data[:-1])

        self.assertEmpty()

        # add the final byte
        self.packet_buffer.add_data(self.digital_data[-1:])

        self.assertNextEventEqual(self.digital_event)

        self.assertEmpty()

    def test_partial_train(self):
        # concat data
        data = b''.join(self.datas)

        # split just after first packet
        data1, data2 = data[:4], data[4:]

        self.packet_buffer.add_data(data1)
        self.assertNextEventEqual(self.digital_event)
        self.assertEmpty()

        self.packet_buffer.add_data(data2)
        self.assertNextEventEqual(self.analog_event)
        self.assertNextEventEqual(self.sysex_message)
        self.assertEmpty()


class DigitalDataTest(FirmataTest):

    def test_port(self):
        self.assertEqual(self.digital_event.port, 9)

    def test_value(self):
        self.assertEqual(self.digital_event.value, 0b10110110)

    def test_repr(self):
        self.assertEqual(
            self.digital_event.__repr__(),
            "<DigitalData port:9, value:0b10110110>"
        )


class AnalogDataTest(FirmataTest):

    def test_pin_number(self):
        self.assertEqual(self.analog_event.pin, 9)

    def test_value(self):
        self.assertEqual(self.analog_event.value, 3456)

    def test_repr(self):
        self.assertEqual(
            self.analog_event.__repr__(),
            "<AnalogData pin:9, value:3456>"
        )


class SysExEventTest(FirmataTest):

    def test_command_byte(self):
        self.assertEqual(self.sysex_message.command, 0x71)

    def test_data(self):
        self.assertEqual(self.sysex_message.data, b'\x54\x00')

    def test_repr(self):
        self.assertEqual(
            self.sysex_message.__repr__(),
            "<SysExMessage command:\\x71, data:\\x54\\x00>"
        )


class ProtocolVersionTest(FirmataTest):

    def setUp(self):
        self.version_data = bytearray([0xf9, 0x02, 0x05])
        self.event = firmata.ProtocolVersion(self.version_data)

    def test_version_numbers(self):
        self.assertEqual(self.event.minor, 5)
        self.assertEqual(self.event.major, 2)

    def test_repr(self):
        self.assertEqual(
            self.event.__repr__(),
            "<ProtocolVersion version:2.5>"
        )


class FirmwareVersionTest(FirmataTest):

    def setUp(self):
        super(FirmwareVersionTest, self).setUp()

        self.report_firmware_message = bytearray(
            b'\xf0y\x02\x08T\x00e\x00s\x00t\x00.\x00i\x00n\x00o\x00\xf7')
        self.report_firmware_sysex = \
            firmata.SysExMessage(self.report_firmware_message)
        self.report_firmware_event = \
            sysex.ReportFirmware(self.report_firmware_sysex)

    def test_version_numbers(self):
        self.assertEqual(self.report_firmware_event.major, 2)
        self.assertEqual(self.report_firmware_event.minor, 8)

    def test_name(self):
        self.assertEqual(self.report_firmware_event.name, 'Test.ino')

    def test_repr(self):
        self.assertEqual(
            self.report_firmware_event.__repr__(),
            "<ReportFirmware version:2.8, name:'Test.ino'>"
        )

    def test_through_connection(self):
        events = self.connection.receive_data(self.report_firmware_message)
        self.assertEventEqual(events[0], self.report_firmware_event)


class StringDataTest(FirmataTest):

    def test_StringData(self):
        self.assertEqual(self.string_sysex.string, 'T')

    def test_str_method(self):
        self.assertEqual(str(self.string_sysex), 'T')

    def test_repr(self):
        self.assertEqual(
            self.string_sysex.__repr__(),
            "<StringData string:'T'>"
        )


class PinStateResponse(FirmataTest):

    def setUp(self):
        # pin 1, mode PIN_MODE_PWM, state 0x3fff (2^14 - 1)
        self.pin_state_bytes = bytearray(b'\xf0\x6e\x01\x03\x7f\x7f\xf7')
        self.pin_state_sysex = firmata.SysExMessage(self.pin_state_bytes)
        self.pin_state_message = sysex.PinStateResponse(self.pin_state_sysex)

    def test_repr(self):
        self.assertEqual(
            self.pin_state_message.__repr__(),
            "<PinStateResponse pin:1, pin_mode:3, pin_state:16383>"
        )


class SysExRegistryTest(FirmataTest):

    def setUp(self):
        super(SysExRegistryTest, self).setUp()
        self.factory = firmata.SysExRegistry()

    def test_to_StringData(self):
        self.assertIsInstance(
            self.factory.from_sysex(self.sysex_message),
            sysex.StringData)

    def test_unkown_sysex(self):
        unknown_sysex = firmata.SysExMessage(
            bytearray(b'\xF0\xDE\xAD\xBE\xEF\xF7'))
        self.assertIs(
            self.factory.from_sysex(unknown_sysex),
            unknown_sysex)


class FirmataConnectionTest(FirmataTest):

    def test_receive_AnalogData(self):
        events = self.connection.receive_data(self.analog_data)
        self.assertEventEqual(events[0], self.analog_event)

    def test_receive_StringData(self):
        events = self.connection.receive_data(self.string_data)
        self.assertEventEqual(events[0], self.string_sysex)

if __name__ == '__main__':
    unittest.main()
