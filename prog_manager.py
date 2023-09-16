from multiprocessing import shared_memory
import sys

def prog_mgr():
	shm_quit = shared_memory.SharedMemory('quit')
	shm_calibration = shared_memory.SharedMemory('calib')
	shm_prog_end_1 = shared_memory.SharedMemory('force')
	#shm_prog_end_2 = shared_memory.SharedMemory('audio')
	
	while True:
		if shm_calibration.buf[:5] == b'ended':
			break
	
	sys.stdin = open(0)
	cmd = input("Press any key then enter to stop recording: ")
	if cmd:
		shm_quit.buf[:5] = b'quit!'
	else:
		shm_quit.buf[:5] = b'quit!'

	print("TERMINATING PROGRAM")
	while shm_prog_end_1.buf[:5] != b'ended': #and shm_prog_end_2.buf[:5] != b'ended':
		print("...")

	shm_quit.close()
	shm_calibration.close()
	shm_prog_end_1.close()
	#shm_prog_end_2.close()
	
if __name__ == '__main__':
	prog_mgr()
