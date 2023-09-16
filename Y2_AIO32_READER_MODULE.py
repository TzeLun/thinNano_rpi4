import smbus
import numpy as np

# ThinNANO calibration matrix, such that F = C * V (unit force, uf)
C = [[0.020724, -0.013852, 0.017362, -0.677410, -0.091951, 0.691302],
	 [-0.018970, 0.793928, 0.031661, -0.393144, 0.033413, -0.381745],
	 [1.345862, -0.008562, 1.335759, 0.000854, 1.362743, -0.001024],
	 [0.000234, 0.077605, 0.762237, -0.034352, -0.771874, -0.037681],
	 [-0.883886, 0.059115, 0.474987, 0.036656, 0.421614, -0.087505],
	 [-0.030817, 0.331622, -0.004021, 0.329045, -0.018001, 0.289065]]
     
# Conversion from unit force to N or Nm
UF_TO_N_CONVF = 9.8 * 10**-3
UF_TO_NM_CONVF = 9.8 * 10**-5

class PCA9554:

    class Register:
        InputPort = 0
        OutputPort = 1
        PolarityInversion = 2
        Configuration = 3

    i2c = smbus.SMBus(1)

    def __init__(self, address):
        self.address = address

    def set_direction(self, value):
        self.i2c.write_byte_data(self.address, self.Register.Configuration , value)

    def write(self, value):
        self.i2c.write_byte_data(self.address, self.Register.OutputPort, value)

class ADS1115:

    class Register:
        Conversion = 0
        Config = 1
        LoThresh = 2
        HiThresh = 3

    class SingleShotCoversion:
        NoEffect = 0
        Begin = 1

    class Mux:
        Ain0_Ain1 = 0
        Ain0_Ain3 = 1
        Ain1_Ain3 = 2
        Ain2_Ain3 = 3
        Ain0_Gnd = 4
        Ain1_Gnd = 5
        Ain2_Gnd = 6
        Ain3_Gnd = 7

    class PGA:
        PGA_6_144V = 0
        PGA_4_096V = 1
        PGA_2_048V = 2
        PGA_1_024V = 3
        PGA_0_512V = 4
        PGA_0_256V = 5

    class Mode:
        Continuous = 0
        PowerDownSingleShot = 1

    class DataRate:
        DR_8SPS = 0
        DR_16SPS = 1
        DR_32SPS = 2
        DR_64SPS = 3
        DR_128SPS = 4 # Default
        DR_250SPS = 5
        DR_475SPS = 6
        DR_860SPS = 7

    class ComparatorQueue:
        Disable = 0x03

    i2c = smbus.SMBus(1)

    def __init__(self, address):
        self.address = address

    def analog_read(self, mux, data_rate, pga):
        self.i2c.write_word_data(self.address, self.Register.Config, data_rate << 13 | self.ComparatorQueue.Disable << 8 | self.SingleShotCoversion.Begin << 7 | mux << 4 | pga << 1 | self.Mode.PowerDownSingleShot)

        data = 0
        while data & 0x80 == 0:
            data = self.i2c.read_byte_data(self.address, 1)

        self.i2c.write_byte_data(self.address, self.Register.Conversion, 1)

        word_data = self.i2c.read_word_data(self.address, self.Register.Conversion)
        data = (word_data << 8) & 0xff00 | (word_data >> 8) & 0xff
        if data >= 0x8000:
            data -= 0x10000
        return data

class AIO_32_0RA_IRC:

    class PGA:
        PGA_10_0352V = ADS1115.PGA.PGA_2_048V
        PGA_5_0176V = ADS1115.PGA.PGA_1_024V
        PGA_2_5088V = ADS1115.PGA.PGA_0_512V
        PGA_1_2544V = ADS1115.PGA.PGA_0_256V

    class DataRate:
        DR_8SPS = ADS1115.DataRate.DR_8SPS
        DR_16SPS = ADS1115.DataRate.DR_16SPS
        DR_32SPS = ADS1115.DataRate.DR_32SPS
        DR_64SPS = ADS1115.DataRate.DR_64SPS
        DR_128SPS = ADS1115.DataRate.DR_128SPS
        DR_250SPS = ADS1115.DataRate.DR_250SPS
        DR_475SPS = ADS1115.DataRate.DR_475SPS
        DR_860SPS = ADS1115.DataRate.DR_860SPS

    multiplexerSettings = 0xff

    def __init__(self, ads1115_address, pca9554_address):
        self.ads1115 = ADS1115(ads1115_address)
        self.multiplexer = PCA9554(pca9554_address)
        self.multiplexerSettings = 0xff
        self.multiplexer.write(self.multiplexerSettings)
        self.multiplexer.set_direction(0)

    def analog_read(self, channel, data_rate, pga):
        if (channel < 16):
            extMux = (self.multiplexerSettings & 0xf0) | channel
            adcMux = ADS1115.Mux.Ain0_Gnd
        elif (channel < 32):
            extMux = (self.multiplexerSettings & 0x0f) | (channel & 0x0f) << 4
            adcMux = ADS1115.Mux.Ain1_Gnd
        elif (channel < 48):
            extMux = (self.multiplexerSettings & 0xf0) | channel
            adcMux = ADS1115.Mux.Ain0_Ain3
        elif (channel < 64):
            extMux = (self.multiplexerSettings & 0x0f) | (channel & 0x0f) << 4
            adcMux = ADS1115.Mux.Ain1_Ain3
        elif (channel < 256):
            return 0
        else:
            extMux = channel & 0xff
            adcMux = ADS1115.Mux.Ain0_Ain1

        if (self.multiplexerSettings != extMux):
            self.multiplexer.write(extMux)
            self.multiplexerSettings = extMux

        return self.ads1115.analog_read(adcMux, data_rate, pga)

    def analog_read_volt(self, channel, data_rate = DataRate.DR_128SPS, pga = PGA.PGA_10_0352V):
        if pga == self.PGA.PGA_1_2544V:
            return float(0.256 * 49 / 10 / 32767 * self.analog_read(channel, data_rate, pga))
        elif pga == self.PGA.PGA_2_5088V:
            return float(0.512 * 49 / 10 / 32767 * self.analog_read(channel, data_rate, pga))
        elif pga == self.PGA.PGA_5_0176V:
            return float(1.024 * 49 / 10 / 32767 * self.analog_read(channel, data_rate, pga))
        else:
            return float(2.048 * 49 / 10 / 32767 * self.analog_read(channel, data_rate, pga))
    
    def read_data(self, pin_config, drate = DataRate.DR_128SPS, pga = PGA.PGA_5_0176V):
        # voltage value: [Fx, Fy, Fz, Tx, Ty, Tz]
        V = []
        # 6 channels for Fx, Fy, Fz, Tx, Ty, Tz
        for channel in pin_config:
            ch = channel * 17 + 256
            v = self.analog_read(ch, drate, pga)
            V.append(v >> 4)
        F = np.matmul(np.array(C), np.array(V))
        F[0] = F[0] * UF_TO_N_CONVF
        F[1] = F[1] * UF_TO_N_CONVF
        F[2] = F[2] * UF_TO_N_CONVF
        F[3] = F[3] * UF_TO_NM_CONVF
        F[4] = F[4] * UF_TO_NM_CONVF
        F[5] = F[5] * UF_TO_NM_CONVF
        return F

    
