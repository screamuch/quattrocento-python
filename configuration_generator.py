# python 3.8

# This is a configuration file for the OT Biolettronica Quattrocento device.
# https://www.otbioelettronica.it/en/products/hardware/quattrocento

# Variables set here will be compiled into a 40-byte packet
# according to the protocol supplied by Bioelettronica (manufacturer).

# Please consult the protocol to correctly set up the configuration bits.
# Protocol: https://otbioelettronica.it/en/?preview=1&option=com_dropfiles&format=&task=frontfile.download&catid=41&id=70&Itemid=1000000000000

# The resulting hexadecimal string can be used outside of this code.

# Default values enable acquisition of data from one 8x8 electrode matrix
# commonly used at ICE Lab (San Francisco State University)

# Peter Chudinov, 2023 - ICE Lab @ San Francisco State University

# -----------------------------------------------------------------------------

# CRC library to compute the checksum at the end of configuration packet
from crc import Calculator, Crc8

# Set number of channels (electrodes) you will use
# This number can be 96, 192, 288, 384
NUMBER_OF_CHANNELS = 288

# Set sampling frequency you will use
# This value must match the bits in ACQ_SETT and can be 512, 2048, 5120, 10240
SAMPLING_FREQUENCY = 2048

# ACQ_SETT
# Sampling frequency, number of channels,
# start/stop acquisition, start/stop recording
ACQ_SETT = "10001101"

# AN_OUT_IN_SEL
# Select the input source and gain for the analog output
AN_OUT_IN_SEL = "00010000"

# AN_OUT_CH_SEL
# Select the channel for the analog output source
AN_OUT_CH_SEL = "00000000"

# INx_CONF0/1/2
# Configuration for the eight IN inputs: high pass filter,
# low pass filter, detection mode, muscle, side, sensor and adapter

# IN1_CONF
IN1_CONF0 = "00000000"
IN1_CONF1 = "00000000"
IN1_CONF2 = "00000000"

# IN2_CONF
IN2_CONF0 = "00000000"
IN2_CONF1 = "00000000"
IN2_CONF2 = "00000000"

# IN3_CONF
IN3_CONF0 = "00000000"
IN3_CONF1 = "00000000"
IN3_CONF2 = "00000000"

# IN4_CONF
IN4_CONF0 = "00000000"
IN4_CONF1 = "00000000"
IN4_CONF2 = "00000000"

# IN5_CONF
IN5_CONF0 = "00000000"
IN5_CONF1 = "00000000"
IN5_CONF2 = "00000000"

# IN6_CONF
IN6_CONF0 = "00000000"
IN6_CONF1 = "00000000"
IN6_CONF2 = "00000000"

# IN7_CONF
IN7_CONF0 = "00000000"
IN7_CONF1 = "00000000"
IN7_CONF2 = "00000000"

# IN8_CONF
IN8_CONF0 = "00000000"
IN8_CONF1 = "00000000"
IN8_CONF2 = "00000000"

# MULTIPLE_INx_CONF0/1/2
# Configuration for the four MULTIPLE IN inputs: high pass filter,
# low pass filter and detection mode, muscle, side, sensor and adapter

# MULTIPLE_IN1_CONF
MULTIPLE_IN1_CONF0 = "00011010"
MULTIPLE_IN1_CONF1 = "00000100"
MULTIPLE_IN1_CONF2 = "10010100"

# MULTIPLE_IN2_CONF
MULTIPLE_IN2_CONF0 = "00011010"
MULTIPLE_IN2_CONF1 = "00000100"
MULTIPLE_IN2_CONF2 = "10010100"

# MULTIPLE_IN3_CONF
MULTIPLE_IN3_CONF0 = "00011010"
MULTIPLE_IN3_CONF1 = "00000100"
MULTIPLE_IN3_CONF2 = "10010100"

# MULTIPLE_IN4_CONF
MULTIPLE_IN4_CONF0 = "00000000"
MULTIPLE_IN4_CONF1 = "00000000"
MULTIPLE_IN4_CONF2 = "00000000"

# Combine configuration bits together
acquisition_binary = \
    ACQ_SETT + \
    AN_OUT_IN_SEL + \
    AN_OUT_CH_SEL + \
    IN1_CONF0 + IN1_CONF1 + IN1_CONF2 + \
    IN2_CONF0 + IN2_CONF1 + IN2_CONF2 + \
    IN3_CONF0 + IN3_CONF1 + IN3_CONF2 + \
    IN4_CONF0 + IN4_CONF1 + IN4_CONF2 + \
    IN5_CONF0 + IN5_CONF1 + IN5_CONF2 + \
    IN6_CONF0 + IN6_CONF1 + IN6_CONF2 + \
    IN7_CONF0 + IN7_CONF1 + IN7_CONF2 + \
    IN8_CONF0 + IN8_CONF1 + IN8_CONF2 + \
    MULTIPLE_IN1_CONF0 + MULTIPLE_IN1_CONF1 + MULTIPLE_IN1_CONF2 + \
    MULTIPLE_IN2_CONF0 + MULTIPLE_IN2_CONF1 + MULTIPLE_IN2_CONF2 + \
    MULTIPLE_IN3_CONF0 + MULTIPLE_IN3_CONF1 + MULTIPLE_IN3_CONF2 + \
    MULTIPLE_IN4_CONF0 + MULTIPLE_IN4_CONF1 + MULTIPLE_IN4_CONF2

# convert into hex
acquisition_hex = hex(int(acquisition_binary, 2))[2:]

# CRC
# Parity check using the CRC-8/MAXIM algorithm
calculator = Calculator(Crc8.MAXIM_DOW)
checksum = hex(calculator.checksum(bytes.fromhex(acquisition_hex)))[2:]

# This method puts everything together
def generate_command():
    msg = acquisition_hex + checksum
    return msg, NUMBER_OF_CHANNELS, SAMPLING_FREQUENCY

if __name__ == "__main__":
    print(generate_command()[0])

