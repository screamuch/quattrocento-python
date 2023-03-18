# python 3.8

# This script will stream data from Quattrocento's TCP socket and print it
# to stdout.

# Please configure acquisition parameters in configuration_generator.py
# before using this file.

# This code has been readopted for use with Quattrocento, initially
# developed for sessantoquattro by OT Bioelettronica

# Peter Chudinov, 2023 - ICE Lab @ San Francisco State University

# -----------------------------------------------------------------------------

import socket
import configuration_generator
import signal

# Network settings
ip_address = '192.168.1.32'    # written on the QC's LCD
port = 23456                    # can be changed in online interface

# Conversion factor to convert byte values into mV
CONVERSION_FACTOR = 0.000286

# Convert integer to bytes
def integer_to_bytes(command):
    return int(command).to_bytes(2, byteorder="big")

# Convert byte-array value to an integer value and apply two's complement
def convert_bytes_to_int(bytes_value, bytes_in_sample):
    value = None
    if bytes_in_sample == 2:
        # Combine 2 bytes to a 16 bit integer value
        value = \
            bytes_value[0] * 256 + \
            bytes_value[1]
        # See if the value is negative and make the two's complement
        if value >= 32768:
            value -= 65536
    elif bytes_in_sample == 3:
        # Combine 3 bytes to a 24 bit integer value
        value = \
            bytes_value[0] * 65536 + \
            bytes_value[1] * 256 + \
            bytes_value[2]
        # See if the value is negative and make the two's complement
        if value >= 8388608:
            value -= 16777216
    else:
        raise Exception(
            "Unknown bytes_in_sample value. Got: {}, "
            "but expecting 2 or 3".format(bytes_in_sample))
    return value


# Generate command for quattrocento's data acquisition
def create_bin_command(start=1):
    # This value is default for quattrocento
    bytes_in_sample = 2

    (start_command,
    number_of_channels,
    sample_frequency) = configuration_generator.generate_command()

    # This command will stop acquisition (last bit of first byte is set to 0)
    if start == 0:
        start_command = "8010000000000000000000000000000000000000000000000000001a04940000000000000000002c"

    return (bytes.fromhex(start_command),
            number_of_channels,
            sample_frequency,
            bytes_in_sample)

# Convert channels from bytes to integers
def bytes_to_integers(
        sample_from_channels_as_bytes,
        number_of_channels,
        bytes_in_sample,
        output_milli_volts):
    channel_values = []
    # Separate channels from byte-string. One channel has
    # "bytes_in_sample" many bytes in it.
    for channel_index in range(number_of_channels):
        channel_start = channel_index * bytes_in_sample
        channel_end = (channel_index + 1) * bytes_in_sample
        channel = sample_from_channels_as_bytes[channel_start:channel_end]

        # Convert channel's byte value to integer
        value = convert_bytes_to_int(channel, bytes_in_sample)

        # Convert bio measurement channels to milli volts if needed
        # The 4 last channels (Auxiliary and Accessory-channels)
        # are not to be converted to milli volts
        if output_milli_volts and channel_index < (number_of_channels - 8):
            value *= CONVERSION_FACTOR
        channel_values.append(value)
    return channel_values


#     Read raw byte stream from data logger. Read one sample from each
#     channel. Each channel has 'bytes_in_sample' many bytes in it.
def read_raw_bytes(connection, number_of_all_channels, bytes_in_sample):
    buffer_size = number_of_all_channels * bytes_in_sample
    new_bytes = connection.recv(buffer_size)

    # Sometimes, packets arrive with incomplete signal data;
    # to mediate that, we just read whatever's missing from the next packet.
    while len(new_bytes) < buffer_size:
        missing_bytes = buffer_size - len(new_bytes)
        new_bytes += connection.recv(missing_bytes)
    return new_bytes

def connect_to_qc(ip_address, port, start_command):
    # use these options for more stable connection (bioelettronica suggestion)
    qc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    qc_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    qc_socket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)

    # establish connection with quattrocento
    qc_socket.connect((ip_address, port))

    # first send command to stop acquisition
    qc_socket.sendall(create_bin_command(start=0)[0])

    # send command to start acquistion
    qc_socket.sendall(start_command)

    return qc_socket

# Disconnect from Quattrocento by sending a stop command
# sq is legacy name used for sessantoquattro
# it works and I will leave it here
def disconnect_from_sq(conn):
    if conn is not None:
        (stop_command,
         _,
         __,
         ___) = create_bin_command(start=0)
        conn.send(stop_command)
        conn.shutdown(2)
        conn.close()
    else:
        raise Exception(
            "Can't disconnect because the"
            "connection is not established")

# on SIGINT stops acquisition and exits program gracefully
def sigint_handler(signum, frame):
    disconnect_from_sq(connection)
    exit(0)

# Read EMG Signal
# Input: socket connected to Quattrocento, acquisition parameters
# Output: array of signals from electrodes
def read_emg_signal(connection, number_of_channels, bytes_in_sample, output_milli_volts=True):
    # 16 zero channels + 8 accessory channels
    number_of_all_channels = number_of_channels + 16 + 8
    buffer_size = number_of_all_channels * bytes_in_sample
    data = read_raw_bytes(connection, number_of_all_channels, bytes_in_sample)
    sample_from_channels = bytes_to_integers(
        data,
        number_of_all_channels,
        bytes_in_sample,
        output_milli_volts)
    return sample_from_channels

# Demo section
if __name__ == "__main__":
    # Create start command and get basic setup information
    (start_command,
     number_of_channels,
     sample_frequency,
     bytes_in_sample) = create_bin_command(start=1)

    connection = connect_to_qc(ip_address, port, start_command)

    # Sends a stop acquisition command to quattrocento on CTRL+C
    # not necessary, but saves battery on the amplifier.
    signal.signal(signal.SIGINT, sigint_handler)

    while True:
        print(read_emg_signal(connection,
                              number_of_channels,
                              bytes_in_sample,
                              output_milli_volts=True))

