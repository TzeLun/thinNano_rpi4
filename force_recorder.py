# Guide URL: https://www.y2c.co.jp/i2c-r/aio-32-0ra-irc/raspberrypi-python/
from Y2_AIO32_READER_MODULE import AIO_32_0RA_IRC
import time
import csv
import numpy as np
from multiprocessing import shared_memory

def force_recorder(arr, pin_config=[0,1,2,3,4,5], t_calib=10, filename="force_data"):
	
	filename = filename + ".csv"
	
	cshm1 = shared_memory.SharedMemory('calib')
	q_shm1 = shared_memory.SharedMemory('quit')
	e_shm1 = shared_memory.SharedMemory('force')

	#DURATION = 10 # controls the duration of the recording
	aio = AIO_32_0RA_IRC(0x49, 0x3e)
	start_time = time.time()

	data = {'Fx':[], 'Fy':[], 'Fz':[], 'Tx':[], 'Ty':[], 'Tz':[]}

	# アナログ入力値の読み出し（電圧値）（128SPS）
	# To read differential analog input
	# Format: channel num * 17 + 256 (channel num is 0 inclusive)
	# Channel num: 256 (0) refers to P1-1 pin and P1-2 pin (+/-)
	calibration_file = open("calibration.txt", "w")
	print("--- START FORCE SENSOR CALIBRATION ---")
	while (time.time() - start_time) <= t_calib:
		print(f"CALIBRATION TIME REMAINING: {round(t_calib - (time.time() - start_time), 3)}s")
		try:
			F = aio.read_data(pin_config)
			#print(F[2])
			data['Fx'].append(F[0])
			data['Fy'].append(F[1])
			data['Fz'].append(F[2])
			data['Tx'].append(F[3])
			data['Ty'].append(F[4])
			data['Tz'].append(F[5])
		except KeyboardInterrupt:
			calibration_file.close()
	calibration_file.write(f"{sum(data['Fx']) / float(len(data['Fx']))}\n")
	calibration_file.write(f"{sum(data['Fy']) / float(len(data['Fy']))}\n")
	calibration_file.write(f"{sum(data['Fz']) / float(len(data['Fz']))}\n")
	calibration_file.write(f"{sum(data['Tx']) / float(len(data['Tx']))}\n")
	calibration_file.write(f"{sum(data['Ty']) / float(len(data['Ty']))}\n")
	calibration_file.write(f"{sum(data['Tz']) / float(len(data['Tz']))}")
	calibration_file.close()

	offset = []

	with open("calibration.txt") as f:
		for line in f.readlines():
			offset.append(float(line))

	#print(offset)

	cshm1.buf[:5] = b'ended'

	print("--- CALIBRATION COMPLETED --- FORCE RECORDING STARTED ---")
	start_time = time.time()
	current_time = 0
	csv_file  = open(filename, 'w')
	writer = csv.writer(csv_file)
	while q_shm1.buf[:5] != b'quit!':
		current_time = time.time() - start_time
		try:
			F = aio.read_data(pin_config)
			F = np.subtract(F, np.array(offset))
			arr[0] = F[0]
			arr[1] = F[1]
			arr[2] = F[2]
			arr[3] = F[3]
			arr[4] = F[4]
			arr[5] = F[5]
			data = np.append(F, current_time)
			writer.writerow(data)
			#print(f"Fx = {F[0]};")
			#print(f"Fy = {F[1]};")
			#print(f"Fz = {F[2]};")
			#print(f"Tx = {F[3]};")
			#print(f"Ty = {F[4]};")
			#print(f"Tz = {F[5]};\n")
		except KeyboardInterrupt:
			csv_file.close()
	csv_file.close()

	print(f"--- FORCE_RECORDER.PY --- TIME TAKEN: {current_time}s")

	e_shm1.buf[:5] = b'ended'

	cshm1.close()
	q_shm1.close()
	e_shm1.close()
	
if __name__ == '__main__':
	force_recorder()
