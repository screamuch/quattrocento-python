import stream_data
import csv, sys

ip_address = "192.168.1.14"
port = 23456

(start_command,
number_of_channels,
sample_frequency,
bytes_in_sample) = stream_data.create_bin_command(start=1)

connection = stream_data.connect_to_qc(ip_address, port, start_command)

file_name = sys.argv[1] + ".csv"
data_file = open(file_name, 'w')
data_file_writer = csv.writer(data_file)

print("Recording 20000 samples...")

for i in range(20000):
    emg_data_frame = stream_data.read_emg_signal(connection,
                            number_of_channels,
                            bytes_in_sample,
                            output_milli_volts=True)

    data_file_writer.writerow(emg_data_frame)
    print(i, end=' ')

print("Done recording")

stream_data.disconnect_from_sq(connection)

