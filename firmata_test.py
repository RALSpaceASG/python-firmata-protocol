#!/usr/bin/env python3
"""
firmata_test.py
~~~~~~~~~~~~~~~

Unit tests for firmata.py.
"""
import unittest

import firmata


class FirmataTest(unittest.TestCase):

    # port 9 bitmask 0b10110110
    digital_data = bytes([0x99, 0b00110110, 0b00000001])
    # analog pin 9 14-bit value 3456
    analog_data = bytes([0xE9, 0x00, 0b11011])
    string_data = bytes([0xF0, 0x71, 0x54, 0x00, 0xF7])

    def setUp(self):
        self.digital_event = firmata.DigitalData(self.digital_data)
        self.analog_event = firmata.AnalogData(self.analog_data)
        self.string_sysex = firmata.SysExMessage(self.string_data)

    def assertEventEqual(self, eventA, eventB):
        '''test if two events are equilavent'''
        # assume that if the representations match, that is sufficient
        self.assertEqual(eventA.__repr__(), eventB.__repr__())


class FirmataPacketBufferTest(FirmataTest):

    def setUp(self):
        super().setUp()
        self.packet_buffer = firmata.FirmataPacketBuffer()

        self.datas = (
            self.digital_data, self.analog_data, self.string_data)
        self.events = (
            self.digital_event, self.analog_event, self.string_sysex)

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

        events = (self.digital_event, self.analog_event, self.string_sysex)

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
        self.assertNextEventEqual(self.string_sysex)
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
        self.assertEqual(self.string_sysex.command, 0x71)

    def test_data(self):
        self.assertEqual(self.string_sysex.data, b'\x00\x54')

    def test_repr(self):
        self.assertEqual(
            self.string_sysex.__repr__(),
            "<SysExMessage command:\\x71, data:\\x00\\x54>"
        )


class ProtocolVersionTest(FirmataTest):

    def setUp(self):
        self.version_data = [0xf9, 0x02, 0x05]
        self.event = firmata.ProtocolVersion(self.version_data)

    def test_version_numbers(self):
        self.assertEqual(self.event.minor, 5)
        self.assertEqual(self.event.major, 2)

    def test_repr(self):
        self.assertEqual(
            self.event.__repr__(),
            "<ProtocolVersion version:2.5>"
        )

if __name__ == '__main__':
    unittest.main()
