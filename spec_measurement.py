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
        self.root = Tk()  # create new tkinter obj
        self._create_interface()
        self.root.mainloop()

    def connect_to_Zolix_monochromator(self):
        """Method to connect to the zolix monochromator. Don't forger to connect usb and turn on the zolix server"""
        zolix_gateway = ZolixGateway(
            "127.0.0.1", 43665
        )  # configure ip address and port of the client
        zolix_gateway.connect_to_server()  # connect to the server
        zolix_gateway.set_usb_mode(True)  # set the mode of communication in USB mode
        qte = (
            zolix_gateway.search_zolix_usb_device()
        )  # search all zolix connected with the server
        serial = zolix_gateway.get_zolix_usb_serial(0)
        zolix_gateway.set_usb_serials(serial)

        zolix_gateway.get_is_open()  # verify if there is an already connected monochromator
        zolix_gateway.open()  # open the communication with the zolix monochromator and the server
        zolix_gateway.get_is_open()  # verify that the connection between the server and the monochromator is on
        self.zolix_gateway = zolix_gateway

    def connect_to_Rigol_oscilloscope(self):
        rigol_gateway = RigolLib.Scope()
        rigol_gateway.auto()
        rigol_gateway.run()
        self.rigol_gateway = rigol_gateway

    def _change_monochromator_wavelength(self, new_wavelength):
        # if self.zolix_gateway:
        #     self.zolix_gateway.move_to_wave(new_wavelength)  # set new wavelength
        #     cur_wave = self.zolix_gateway.get_current_wave()  # get current wavelength
        #     if cur_wave == new_wavelength:  # check whether the wavelength is set
        #         return True
        # return False
        return True

    def set_oscilloscope_chanel(self):
        val = self.channel_selection.get()
        self.oscilloscope_chanel = val

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
    def _validate_wl_input_float_only(self, P):
        if P.isdigit() or (P and P.replace(".", "", 1).isdigit()) or not P:
            return True
        else:
            return False

    def _start_measurement(self):
        self.initial_wl = float(self.wavelength_from_input.get())
        self.final_wl = float(self.wavelength_to_input.get())
        self.step = float(self.wavelength_measurement_step_input.get())
        self.animationObj = self.plot()

    def _create_interface(self):
        root = self.root

        # root.attributes("-fullscreen", True)  # make fullscreen window
        root.title("Спектрометр")  # give window name
        validate_float_only = (root.register(self._validate_wl_input_float_only), "%P")

        self.opts = {"padx": 10, "pady": 10, "ipadx": 10, "ipady": 10, "sticky": "nswe"}
        opts = self.opts

        self.channel_selection = StringVar(value='ch1')
        ch1_button = Radiobutton(root, text='ch1', variable=self.channel_selection, value='ch1', command=self.set_oscilloscope_chanel)
        ch1_button.grid(row=5, column=1, **opts)
        ch1_button = Radiobutton(root, text='ch2', variable=self.channel_selection, value='ch2', command=self.set_oscilloscope_chanel)
        ch1_button.grid(row=5, column=2, **opts)

        # Создание поля ввода
        self.wavelength_from_label = Label(text="Начальная длина волны")
        self.wavelength_from_label.grid(row=0, column=0, **opts)

        self.wavelength_from_input = Entry(
            validate="key", validatecommand=validate_float_only
        )
        self.wavelength_from_input.grid(row=1, column=0, **opts)

        self.wavelength_to_label = Label(text="Конечная длина волны")
        self.wavelength_to_label.grid(row=0, column=1, **opts)

        self.wavelength_to_input = Entry(
            validate="key",
            validatecommand=validate_float_only,
        )
        self.wavelength_to_input.grid(row=1, column=1, **opts)

        self.wavelength_measurement_step_label = Label(text="Шаг измерения")
        self.wavelength_measurement_step_label.grid(row=0, column=2, **opts)

        self.wavelength_measurement_step_input = Entry(
            validate="key", validatecommand=validate_float_only
        )
        self.wavelength_measurement_step_input.grid(row=1, column=2, **opts)

        # Создание кнопку для начала измерения
        self.start_measurement_button = Button(
            text="Начать измерение", command=self._start_measurement
        )
        self.start_measurement_button.grid(row=3, column=0, columnspan=3, **opts)

    def plot(self):
        # Включаем интерактивный режим
        plt.ion()

        # Создаем объект графика
        fig = plt.Figure()
        ax = fig.add_subplot(111)

        # Устанавливаем границы графика
        ax.set_xlim(self.initial_wl, self.final_wl)
        ax.set_ylim(self.get_Rigol_oscillograph_min_V(), self.get_Rigol_oscillograph_max_V())

        # формируем список точек для измерения
        x_range = np.arange(self.initial_wl, self.final_wl + self.step, self.step)

        progressbar = ttk.Progressbar(
            orient="horizontal", maximum=len(x_range), length=300
        )
        progressbar.grid(row=4, column=0, columnspan=3)

        # Первоначальные данные графика
        x_values = []
        y_values = []

        # Формируем первичную линию графика
        (line1,) = ax.plot(x_values, y_values, "b-")

        # Добавляем наш график в окно
        canvas = FigureCanvasTkAgg(fig, master=self.root)

        # Располагаем график в Tkinter окне
        canvas.get_tk_widget().grid(row=5, column=0, columnspan=3, **self.opts)

        # Пробегаемся по точкам измерения и получаем данные с приборов, и обновляем график
        for x in x_range:
            # if change_monochromator_wavelength(x):
            if self._change_monochromator_wavelength(x):
                progressbar.step(1)
                x_values.append(x)
                y_values.append(self.get_Rigol_oscillograph_average_V())

                line1.set_xdata(x_values)
                line1.set_ydata(y_values)

                # Обновляем график
                fig.canvas.draw()
                fig.canvas.flush_events()
