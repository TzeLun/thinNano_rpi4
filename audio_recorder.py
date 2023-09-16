import pyaudio
import wave
from multiprocessing import shared_memory

def audio_recorder(config, filename="audio_recording"):
	cshm2 = shared_memory.SharedMemory('calib')
	q_shm2 = shared_memory.SharedMemory('quit')
	e_shm2 = shared_memory.SharedMemory('audio')

	CHUNK = config[0]
	FORMAT = pyaudio.paInt16
	CHANNELS = config[1]  # USB Microphone "USB PnP Sound Device" uses only 1 input channel
	RATE = config[2]
	input_device_index= 1  # change the index corresponding to USB microphone
	#RECORD_SECONDS = 20
	WAVE_OUTPUT_FILENAME = filename + ".wav"

	p = pyaudio.PyAudio()

	# Uncomment below to get the details about the sound devices in this PC
	#for i in range(p.get_device_count()):
	#    dev = p.get_device_info_by_index(i)
	#    print((i, dev['name'], dev['maxInputChannels']))

	while True:
		if cshm2.buf[:5] == b'ended':
			print("--- CALIBRATION COMPLETED --- AUDIO RECORDING STARTED ---")
			stream = p.open(format=FORMAT,
					channels=CHANNELS,
					rate=RATE,
					input=True,
					frames_per_buffer=CHUNK)

			frames = []
			
			while q_shm2.buf[:5] != b'quit!':
				data = stream.read(CHUNK)
				frames.append(data)
				
			stream.stop_stream()
			stream.close()
			p.terminate()
			break

	wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(p.get_sample_size(FORMAT))
	wf.setframerate(RATE)
	wf.writeframes(b''.join(frames))
	wf.close()
	
	print(f"--- AUDIO_RECORDER.PY --- TIME TAKEN: {CHUNK / RATE * len(frames)}s")

	e_shm2.buf[:5] = b'ended'

	cshm2.close()
	q_shm2.close()
	e_shm2.close()

if __name__ == '__main__':
	audio_recorder()
