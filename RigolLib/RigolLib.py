import time

import numpy as np
import pyvisa as visa

# Rigol ids
VID = "1AB1"
PID = "0588"

# read -чтение информации из прибора,
# write -запись информации в прибор,
# query -запись команды и, сразу затем, чтение возвращаемого результата.


class Scope(object):
    """Class for Rigol oscilloscope."""

    VID = "1AB1"
    PID = "0588"

    def __init__(self):
        self._time_scale = None
        self.rm = visa.ResourceManager()

    def auto_connect_device(self):
        devices = self.get_available_usb_devices()
        self.scope = None
        for device in devices:
            if self.connect_to_the_Rigol(device):
                break
        if self.scope is None:
            raise ValueError("Не удалось найти устройство")
        print("Установлена связь с устройством", self.res)
        self.create_channels()

    def manual_connect_device(self, device):
        if self.connect_to_the_Rigol(device):
            print("Установлена связь с устройством", self.res)
            self.create_channels()
        else:
            raise ValueError("Не удалось найти устройство")

    def get_available_usb_devices(self):
        return list(self.rm.list_resources())

    def create_channels(self):
        # создаем канал 1 и канал 2
        self.ch1 = Channel(1, self)
        self.ch2 = Channel(2, self)

    def connect_to_the_Rigol(self, device):
        if VID in device and PID in device:
            # сохраняем устройство
            self.scope = self.rm.open_resource(device)
            # получаем информацию об устройстве
            self.res = self.scope.query("*IDN?")
            # включаем автоматическую настройку каналов осциллографа
            self.scope.write(":AUTO")
            time.sleep(6)
            return True
        else:
            return False

    def __del__(self):
        self.close_connection()

    def auto(self):
        """Command the device to automatically select gain and frequency settings."""
        self.write(":AUTO")

    def close_connection(self):
        """Closes all connections"""
        rm = visa.ResourceManager()
        rm.close()

    def query(self, command):
        """Send a command and read the subsequent response as a string."""
        return self.scope.query(command)

    def query_binary(self, command, datatype):
        """Send a command and read the subsequent response as a binary data."""
        return self.scope.query_binary_values(command, datatype)

    def read(self, n=-1):
        """Read data from device as raw bytes."""
        data = self.scope.read(n)
        return data

    def get_acquire_mode(self):
        self._acquire_mode = self.query(":ACQ:MODE ?")
        return self._acquire_mode

    def get_averages(self):
        self._averages = int(self.query(":ACQ:AVER?"))
        return self._averages

    def get_keys_locked(self):
        """Query the key lock status.

        Locked is remote operation (indicated on the oscilloscope display by 'Rmt'.
        Unlocked allows control of the oscilloscope by the front panel keys.
        """
        self._keys_locked = [True if self.ask(":KEY:LOCK?") == "ENAB" else False]
        return self._keys_locked

    def get_mem_depth(self):
        self._mem_depth = int(self.query(":ACQ:MEM?"))
        return self._mem_depth

    def get_time_data(self):
        time_scale = self.get_time_data()
        time = np.arange(
            -300.0 / 50 * time_scale, 300.0 / 50 * time_scale, time_scale / 50
        )
        return time

    def get_time_mode(self):
        self._time_mode = self.query(":TIM:MODE?")
        return self._time_mode

    def get_time_offset(self):
        """Returns time offset (смещение)"""
        self._time_off_set = self.query(":TIM:DEL?")
        return self._time_off_set

    def get_time_scale(self):
        """Read scale of horizontal time ox"""
        self._time_scale = float(self.query(":TIM:SCAL?"))
        return self._time_scale

    def set_acquire_mode(self, mode):
        upper_mode = str(mode).upper()
        if upper_mode in ["NORM, AVER, PEAK"]:
            self.write(f":ACQ:MODE {upper_mode:4s}")
            self._acquire_mode = self.get_acquire_mode()

    def set_averages(self, n_averages):
        if n_averages in [2**p for p in range(1, 8)]:
            self.write(f":ACQ:AVER {n_averages:d}")
            self._averages = self.get_averages()

    def set_keys_locked(self, lock):
        """Set the key lock status.

        Valid options arguments for `lock` are:
        'ENAB' (control over USB connection only)
        'DIS' (local control via oscilloscope front panel keys)
        """
        val = ["ENAB" if lock else "DIS"]
        self.write(f":KEY:LOCK {val:s}")
        self._keys_locked = [True if val == "ENAB" else False]

    def set_mem_depth(self, depth):
        upper_depth = str(depth).upper()
        if upper_depth in ["NORM", "LONG"]:
            self.write(":ACQ:MEM {upper_depth:4s}")
            self._memDepth = self.set_mem_depth()

    def set_time_mode(self, t_mode):
        upper_t_mode = str(t_mode).upper()
        if upper_t_mode in ["MAIN", "DELAYED"]:
            self.write(f":TIM:MODE {upper_t_mode:s}")
            self._timemode = self.timemode

    def set_time_offset(self, delay):
        self.write(f":TIM:DEL {delay:11.9f}")
        self._timeoffset = self._timeoffset

    def set_time_scale(self, seconds_per_div):
        self.write(f":TIM:SCAL {seconds_per_div:11.9f}")
        self._timescale = self.timescale

    def run(self):
        """Command the device to resume sampling."""
        self.write(":RUN")

    def write(self, command):
        """Send a command."""
        self.scope.write(command)
        time.sleep(0.01)
        return


class Channel(object):
    """Create channel objects for channel specific queries."""

    def __init__(self, channel_number, parent):
        self._current_data = None
        self._vertical_scale = None
        self.p = parent
        self.chn = channel_number

    def get_ch_mem_depth(self):
        self._ch_mem_depth = self.p.query(f":CHAN{self.chn:d}:MEM?")
        return self._ch_mem_depth

    def get_current_vertical_data(self):
        binary_data = self.p.query_binary(f":WAV:DATA? CHAN{self.chn:d}", datatype="B")
        vertical_scale = self.get_vertical_scale()
        self._current_data = (255 - np.array(binary_data)) * vertical_scale / 25.0

    def get_vertical_scale(self):
        """Returns vault scale"""
        self._vertical_scale = float(self.p.query(f":CHAN{self.chn:d}:SCAL?"))
        return self._vertical_scale

    def get_vertical_offset(self):
        """Returns vault offset (смещение)"""
        self._vertical_offset = float(self.p.query(f":CHAN{self.chn:d}:OFFS?"))
        return self._vertical_offset

    def set_ch_mem_depth(self, depth):
        self.p.write(":CHAN{self.chn:d}:MEM {depth:d}")
        self._ch_mem_depth = self.get_ch_mem_depth()

    def set_vertical_scale(self, volts_per_div):
        self.p.write(f":CHAN{self.chn:d}:SCAL {volts_per_div:11.9f}")
        self._vertical_scale = self.get_vertical_scale()

    def set_vertical_offset(self, volts):
        self.p.write(f":CHAN{self.chn:d}:OFFS {volts:11.9f}")
        self._vertical_offset = self.get_vertical_offset()

    def meas_Vpp(self):
        return float(self.p.query(f":MEAS:VPP? CHAN{self.chn:d}"))

    def meas_Vmax(self):
        return float(self.p.query(f":MEAS:VMAX? CHAN{self.chn:d}"))

    def meas_Vmin(self):
        return float(self.p.query(f":MEAS:VMIN? CHAN{self.chn:d}"))

    def meas_Vamp(self):
        return float(self.p.query(f":MEAS:VAMP? CHAN{self.chn:d}"))

    def meas_Vtop(self):
        return float(self.p.query(f":MEAS:VTOP? CHAN{self.chn:d}"))

    def meas_Vbase(self):
        return float(self.p.query(f":MEAS:VBAS? CHAN{self.chn:d}"))

    def meas_Vavg(self):
        return float(self.p.query(f":MEAS:VAV? CHAN{self.chn:d}"))

    def meas_Vrms(self):
        return float(self.p.query(f":MEAS:VRMS? CHAN{self.chn:d}"))

    def meas_over(self):
        return float(self.p.query(f":MEAS:OVER? CHAN{self.chn:d}"))

    def meas_pre(self):
        return float(self.p.query(f":MEAS:PRE? CHAN{self.chn:d}"))

    def meas_freq(self):
        return float(self.p.query(f":MEAS:FREQ? CHAN{self.chn:d}"))

    def meas_rise(self):
        return float(self.p.query(f":MEAS:RIS? CHAN{self.chn:d}"))

    def meas_fall(self):
        return float(self.p.query(f":MEAS:FALL? CHAN{self.chn:d}"))

    def meas_period(self):
        return float(self.p.query(f":MEAS:PER? CHAN{self.chn:d}"))

    def meas_posWidth(self):
        return float(self.p.query(f":MEAS:PWID? CHAN{self.chn:d}"))

    def meas_negWidth(self):
        return float(self.p.query(f":MEAS:NWID? CHAN{self.chn:d}"))

    def meas_posDuty(self):
        return float(self.p.query(f":MEAS:PDUT? CHAN{self.chn:d}"))

    def meas_negDuty(self):
        return float(self.p.query(f":MEAS:NDUT? CHAN{self.chn:d}"))

    def meas_posDelay(self):
        return float(self.p.query(f":MEAS:PDE? CHAN{self.chn:d}"))

    def meas_negDelay(self):
        return float(self.p.query(f":MEAS:NDE? CHAN{self.chn:d}"))
