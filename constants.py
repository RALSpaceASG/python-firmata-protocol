"""
firmata-protocol/constants.py
~~~~~~~~~~~~

Constants from Firmata.h needed for the firmata protocol.
"""

START_SYSEX = 0xF0  # start a MIDI Sysex message
END_SYSEX = 0xF7  # end a MIDI Sysex message

# messages from firmata
DIGITAL_MESSAGE = 0x90  # send or receive data for a digital pin
ANALOG_MESSAGE = 0xE0  # send or receive data for a PWM configured pin
PROTOCOL_VERSION = 0xF9  # report protocol version

SERVO_CONFIG = 0x70  # set servo pin and max and min angles
STRING_DATA = 0x71  # a string message with 14-bits per char
STEPPER_DATA = 0x72  # Stepper motor command
I2C_REQUEST = 0x76  # send an I2C read/write request
I2C_REPLY = 0x77  # a reply to an I2C read request
I2C_CONFIG = 0x78  # config I2C settings such as delay times and power pins
REPORT_FIRMWARE = 0x79  # report name and version of the firmware
SAMPLING_INTERVAL = 0x7A  # modify the sampling interval

EXTENDED_ANALOG = 0x6F  # analog write (PWM, Servo, etc) to any pin
PIN_STATE_QUERY = 0x6D  # ask for a pin's current mode and value
PIN_STATE_RESPONSE = 0x6E  # reply with pin's current mode and value
CAPABILITY_QUERY = 0x6B  # ask for supported modes of all pins
CAPABILITY_RESPONSE = 0x6C  # reply with supported modes and resolution
ANALOG_MAPPING_QUERY = 0x69  # ask for mapping of analog to pin numbers
ANALOG_MAPPING_RESPONSE = 0x6A  # reply with analog mapping data
