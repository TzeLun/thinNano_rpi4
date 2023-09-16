from multiprocessing import shared_memory, Process, Array
from force_recorder import force_recorder
from audio_recorder import audio_recorder
from real_time_monitor import force_monitor
from prog_manager import prog_mgr
import datetime

##################################################################
##                 Only edit the section below                  ##
##################################################################

# Configuration of the audio recording:
CHUNK = 1024
CHANNELS = 1  # USB Microphone "USB PnP Sound Device" uses only 1 input channel
RATE = 44100
config = [CHUNK, CHANNELS, RATE]

# Pin connection for the Fx, Fy, Fz, Tx, Ty, Tz wiring
# If connected in order across the first 6 pins,
# The channel number is given below:
# More details at: https://www.y2c.co.jp/i2c-r/aio-32-0ra-irc/raspberrypi-python/
pin_config = [0, 1, 2, 3, 4, 5] 

# Calibration duration of the force sensor (seconds)
calibration_duration = 10

# Filename for the audio and force recorder. May provide a path.
# Do not add the file format at the suffix.
# Default file format is ".csv" for force data and ".wav" for audio
force_filename = "force_" + datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
audio_filename = "audio_" + datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")

force_path = "force_recordings/"
audio_path = "audio_recordings/"

force_filename = force_path + force_filename
audio_filename = audio_path + audio_filename

# Edit the lower and upper error margin of the force monitor plot
# Also adjust the number of data points to be plotted every cycle
n_points = 150
eb = [(-1.5, 1.5), (-1.5, 1.5), (-1.5, 1.5)]  # Set err margin independently
ylim = [(-15.0, 15.0), (-15.0, 15.0), (-15.0, 15.0)]  # Adjust the y-axis limits
nplt = ["Fx","Fy", "Fz"]  # which plots for display

#####################################################################
##                   End of configuration section                  ##
#####################################################################

shm_quit = shared_memory.SharedMemory(create=True, size=10, name='quit')
shm_calibration = shared_memory.SharedMemory(create=True, size=10, name='calib')
shm_prog_end_1 = shared_memory.SharedMemory(create=True, size=10, name='force')
#shm_prog_end_2 = shared_memory.SharedMemory(create=True, size=10, name='audio')

print(f"shared_memory named <{shm_quit.name}> created\n")
print(f"shared_memory named <{shm_calibration.name}> created\n")
print(f"shared_memory named <{shm_prog_end_1.name}> created\n")
#rint(f"shared_memory named <{shm_prog_end_2.name}> created\n")

arr = Array('d', [999] * 6)  # shared memory Array

shm_quit.buf[:5] = b'start'
shm_calibration.buf[:5] = b'start'
shm_prog_end_1.buf[:5] = b'start'
#shm_prog_end_2.buf[:5] = b'start'

processes = []
processes.append(Process(target=force_recorder, args=(arr, pin_config, calibration_duration, force_filename)))
#processes.append(Process(target=audio_recorder, args=(config, audio_filename)))
processes.append(Process(target=force_monitor, args=(arr, n_points, eb, nplt, ylim)))
processes.append(Process(target=prog_mgr))

for process in processes:
	process.start()

for process in processes:
	process.join()

shm_quit.close()
shm_calibration.close()
shm_prog_end_1.close()
#shm_prog_end_2.close()

shm_quit.unlink()
shm_calibration.unlink()
shm_prog_end_1.unlink()
#shm_prog_end_2.unlink()

print("PROGRAM ENDED")
