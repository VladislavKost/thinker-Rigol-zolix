import ipaddress
import random
from tkinter import *
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from zolix.app.zolix_gateway import ZolixGateway
from RigolLib import RigolLib


class SpectralMeasurements:
    """Class for creating window to measure spectre of the sample using oscilloscope and monochromator"""

    def __init__(self):
        self.zolix_gateway = None
        self.rigol_gateway = RigolLib.Scope()
        self.zolix_IP_value = "127.0.0.1"
        self.oscilloscope_chanel = "ch1"

        self.root = Tk()  # create new tkinter obj
        self._create_interface()
        self.root.mainloop()

    def _connect_to_Zolix_monochromator(self):
        """Method to connect to the zolix monochromator. Don't forger to connect usb and turn on the zolix server"""
        if self._validate_IP_zolix():
            # zolix_gateway = ZolixGateway(
            #     f"{self.zolix_IP.get()}", 43665
            # )  # configure ip address and port of the client
            # zolix_gateway.connect_to_server()  # connect to the server
            # zolix_gateway.set_usb_mode(True)  # set the mode of communication in USB mode
            # qte = (
            #     zolix_gateway.search_zolix_usb_device()
            # )  # search all zolix connected with the server
            # serial = zolix_gateway.get_zolix_usb_serial(0)
            # zolix_gateway.set_usb_serials(serial)

            # zolix_gateway.get_is_open()  # verify if there is an already connected monochromator
            # zolix_gateway.open()  # open the communication with the zolix monochromator and the server
            # zolix_gateway.get_is_open()  # verify that the connection between the server and the monochromator is on
            # self.zolix_gateway = zolix_gateway
            self.zolix_connect_state.config(text="Подключено", foreground="#000000")
            return True
        else:
            self.zolix_connect_state.config(
                text="Неверный формат IP адреса.", foreground="#B71C1C"
            )

    def _connect_to_Rigol_oscilloscope(self):
        # self.rigol_gateway.
        # rigol_gateway.auto()
        # rigol_gateway.run()
        # self.rigol_gateway = rigol_gateway
        self.rigol_connect_state.config(text="Подключено")

    def _change_monochromator_wavelength(self, new_wavelength):
        # if self.zolix_gateway:
        #     self.zolix_gateway.move_to_wave(new_wavelength)  # set new wavelength
        #     cur_wave = self.zolix_gateway.get_current_wave()  # get current wavelength
        #     if cur_wave == new_wavelength:  # check whether the wavelength is set
        #         return True
        # return False
        return True

    def _set_oscilloscope_chanel(self, event):
        val = self.channels_selection_box.get()
        self.oscilloscope_chanel = val

    def _set_device_for_Rigol(self, event):
        val = self.rigol_usb_chosen.get()
        self.rigol_device = val

    def get_Rigol_oscillograph_average_V(self):
        # if self.rigol_gateway:
        #     if self.oscilloscope_chanel == "ch1":
        #         return self.rigol_gateway.ch1.meas_Vavg()
        #     elif self.oscilloscope_chanel == "ch2":
        #         return self.rigol_gateway.ch2.meas_Vavg()
        return random.randint(1, 10)

    def get_Rigol_oscillograph_max_V(self):
        # if self.rigol_gateway:
        #     if self.oscilloscope_chanel == "ch1":
        #         return self.rigol_gateway.ch1.meas_Vmax()
        #     elif self.oscilloscope_chanel == "ch2":
        #         return self.rigol_gateway.ch2.meas_Vmax()
        return 10

    def get_Rigol_oscillograph_min_V(self):
        # if self.rigol_gateway:
        #     if self.oscilloscope_chanel == "ch1":
        #         return self.rigol_gateway.ch1.meas_Vmin()
        #     elif self.oscilloscope_chanel == "ch2":
        #         return self.rigol_gateway.ch2.meas_Vmin()
        return 0

    def _validate_wl_input_float_only(self, string):
        if (
            string.isdigit()
            or (string and string.replace(".", "", 1).isdigit())
            or not string
        ):
            return True
        else:
            return False

    def _validate_IP_zolix(self):
        try:
            ipaddress.IPv4Network(self.zolix_IP.get())
            return True
        except ValueError:
            return False

    def _start_measurement(self):
        self.initial_wl = float(self.wavelength_from_input.get())
        self.final_wl = float(self.wavelength_to_input.get())
        self.step = float(self.wavelength_measurement_step_input.get())
        self.animationObj = self.plot()

    def _create_interface(self):
        root = self.root

        root.title("Спектрометр")  # give window name
        validate_float_only = (root.register(self._validate_wl_input_float_only), "%P")

        self.opts = {"padx": 10, "pady": 10, "ipadx": 10, "ipady": 10, "sticky": "nswe"}
        opts = self.opts

        # IP for Zolix
        self.zolix_IP = Entry(root)
        self.zolix_IP.insert(0, self.zolix_IP_value)
        self.zolix_IP.grid(row=0, column=0, **opts)

        # Zolix connect
        self.zolix_connect = Button(
            text="Подключить Zolix", command=self._connect_to_Zolix_monochromator
        )
        self.zolix_connect.grid(row=0, column=1, **opts)

        # Zolix connect state
        self.zolix_connect_state = Label(text="Отключено")
        self.zolix_connect_state.grid(row=0, column=2, **opts)

        # Rigol USB Options
        self.rigol_usb_chosen = ttk.Combobox(
            values=self.rigol_gateway.get_available_usb_devices(),
        )

        # self.rigol_usb_chosen.current(0)
        self.rigol_usb_chosen.grid(row=1, column=0, **opts)
        self.rigol_usb_chosen.bind("<<ComboboxSelected>>", self._set_device_for_Rigol)

        # Rigol USB connect
        self.rigol_connect = Button(
            text="Подключить Rigol", command=self._connect_to_Rigol_oscilloscope
        )
        self.rigol_connect.grid(row=1, column=1, **opts)

        # Rigol connect state
        self.rigol_connect_state = Label(text="Отключено")
        self.rigol_connect_state.grid(row=1, column=2, **opts)

        # Oscilloscope channel selection label
        self.channel_selection_label = Label(
            text="Канал осциллографа"
        )
        self.channel_selection_label.grid(row=2, column=0, **opts)

        # Oscilloscope channel selection
        self.channels_selection_box = ttk.Combobox(
            values=["ch1", "ch2"],
        )
        self.channels_selection_box.current(0)
        self.channels_selection_box.grid(row=2, column=1, **opts)
        self.channels_selection_box.bind(
            "<<ComboboxSelected>>", self._set_oscilloscope_chanel
        )

        # label for initial wavelength
        self.wavelength_from_label = Label(text="Начальная длина волны")
        self.wavelength_from_label.grid(row=4, column=0, **opts)

        # input for initial wavelength
        self.wavelength_from_input = Entry(
            validate="key", validatecommand=validate_float_only
        )
        self.wavelength_from_input.grid(row=5, column=0, **opts)

        # label for final wavelength
        self.wavelength_to_label = Label(text="Конечная длина волны")
        self.wavelength_to_label.grid(row=4, column=1, **opts)

        # input for final wavelength
        self.wavelength_to_input = Entry(
            validate="key",
            validatecommand=validate_float_only,
        )
        self.wavelength_to_input.grid(row=5, column=1, **opts)

        # label for step of wavelengths
        self.wavelength_measurement_step_label = Label(text="Шаг измерения")
        self.wavelength_measurement_step_label.grid(row=4, column=2, **opts)

        # input for step of wavelengths
        self.wavelength_measurement_step_input = Entry(
            validate="key", validatecommand=validate_float_only
        )
        self.wavelength_measurement_step_input.grid(row=5, column=2, **opts)

        # start measurement button
        self.start_measurement_button = Button(
            text="Начать измерение", command=self._start_measurement
        )
        self.start_measurement_button.grid(row=6, column=0, columnspan=3, **opts)

    def plot(self):
        # Включаем интерактивный режим
        plt.ion()

        # Создаем объект графика
        fig = plt.Figure()
        ax = fig.add_subplot(111)

        # Устанавливаем границы графика
        ax.set_xlim(self.initial_wl, self.final_wl)
        ax.set_ylim(
            self.get_Rigol_oscillograph_min_V(), self.get_Rigol_oscillograph_max_V()
        )

        # формируем список точек для измерения
        x_range = np.arange(self.initial_wl, self.final_wl + self.step, self.step)

        # Первоначальные данные графика
        x_values = []
        y_values = []

        # Формируем первичную линию графика
        (line1,) = ax.plot(x_values, y_values, "b-")

        # Добавляем наш график в окно
        canvas = FigureCanvasTkAgg(fig, master=self.root)

        # Располагаем график в Tkinter окне
        canvas.get_tk_widget().grid(row=7, column=0, columnspan=3, **self.opts)

        # Пробегаемся по точкам измерения и получаем данные с приборов, и обновляем график
        for x in x_range:
            # if change_monochromator_wavelength(x):
            if self._change_monochromator_wavelength(x):
                x_values.append(x)
                y_values.append(self.get_Rigol_oscillograph_average_V())

                line1.set_xdata(x_values)
                line1.set_ydata(y_values)

                # Обновляем график
                fig.canvas.draw()
                fig.canvas.flush_events()
