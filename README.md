# thinNano_rpi4
Force and audio recorder program using the Raspberry Pi 4 and the thinNano force sensor.

## Setup
Need `smbus` module. Check [here](https://pypi.org/project/smbus/) for more info. Involves python's multiprocessing module and shared memory, hence `python=>3.9` is mandatory.

## How to run
Launch the script as shown in the line below:
```bash
python drill_force_audio_recorder.py
```

Currently, the audio recording segment is commented out. To use it make sure to uncomment all the related functions in `drill_force_audio_recorder.py` and `prog_manager.py`. Make sure the variable, `pin_config` first defined in line 22 in `drill_force_audio_recorder.py` is set to the correct wiring port. The latest pin_config should be `[7, 8, 9, 10, 11, 12]`.

## Customization
There are some parameters to adjust according to one's liking from `line 12` to `line 44`. For example, the default force sensor calibration code runs for 10s and tuning `calibration_duration` in `line 25` will alter it.

## Terminating the recordings
To ensure a safe termination of the running script, follow the instruction at the terminal running this script. If it isn't clear, just press enter to terminate the program.
