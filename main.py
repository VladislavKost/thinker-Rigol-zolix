from tkinter import *
from tkinter import ttk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.animation as animation
import numpy as np
import time
import random
from collections import deque


def validate_wl_input(P):
    if P.isdigit() or (P and P.replace(".", "", 1).isdigit()) or not P:
        return True
    else:
        return False


def set_monochromator_wavelength(new_wl):
    time.sleep(1)
    return True


def get_oscillograph_data():
    return random.randint(1, 10)


def plot(initial_wl, final_wl, step):
    # Включаем интерактивный режим
    plt.ion()

    # Создаем объект графика
    fig = plt.Figure()
    ax = fig.add_subplot(111)

    # Устанавливаем границы графика
    ax.set_xlim(initial_wl, final_wl)
    ax.set_ylim(0, 10)

    # формируем список точек для измерения
    x_range = np.arange(initial_wl, final_wl, step)

    progressbar =  ttk.Progressbar(orient="horizontal", maximum=len(x_range), length=300)
    progressbar.grid(row=4,column=0, columnspan=3)

    # Первоначальные данные графика
    x_values = []
    y_values = []

    # Формируем первичную линию графика
    (line1,) = ax.plot(x_values, y_values, "b-")

    # Добавляем наш график в окно
    canvas = FigureCanvasTkAgg(fig, master=root)

    # Располагаем график в Tkinter окне
    canvas.get_tk_widget().grid(row=5, column=0, columnspan=3, **opts)

    # Пробегаемся по точкам измерения и получаем данные с приборов, и обновляем график
    for x in x_range:
        if set_monochromator_wavelength(x):
            progressbar.step(1)
            x_values.append(x)
            y_values.append(get_oscillograph_data())

            line1.set_xdata(x_values)
            line1.set_ydata(y_values)

            # Обновляем график
            fig.canvas.draw()
            fig.canvas.flush_events()

    toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=True)
    toolbar.update()
    # toolbar.pack(side=BOTTOM, fill=X)


def start_measurement():
    global animationObj
    initial_wl = float(wavelength_from_input.get())
    final_wl = float(wavelength_to_input.get())
    step = float(wavelength_measurement_step_input.get())
    animationObj = plot(initial_wl, final_wl, step)


# Создаем окно
root = Tk()

# Получаем параметры экрана: ширину и высоту
w = root.winfo_screenwidth()
h = root.winfo_screenheight()

# Добавляем имя окна и его размер. Не забываем отцентрировать отняв половину ширины окна
root.title("Спектрометр")
root.geometry(f"{w}x{h}")

# Создание регулярного выражения для валидации ввода
validate_float_only = (root.register(validate_wl_input), "%P")

opts = { 'padx': 10, 'pady': 10, 'ipadx': 10, 'ipady': 10 , 'sticky': 'nswe' }

# Создание поля ввода
wavelength_from_label = Label(text="Начальная длина волны")
wavelength_from_label.grid(row=0, column=0, **opts)

wavelength_from_input = Entry(validate="key", validatecommand=validate_float_only)
wavelength_from_input.grid(row=1, column=0, **opts)

wavelength_to_label = Label(text="Конечная длина волны")
wavelength_to_label.grid(row=0, column=1, **opts)

wavelength_to_input = Entry(validate="key", validatecommand=validate_float_only,)
wavelength_to_input.grid(row=1, column=1, **opts)

wavelength_measurement_step_label = Label(text="Шаг измерения")
wavelength_measurement_step_label.grid(row=0, column=2, **opts)

wavelength_measurement_step_input = Entry(
    validate="key", validatecommand=validate_float_only
)
wavelength_measurement_step_input.grid(row=1, column=2, **opts)

# Создание кнопку для начала измерения
start_measurement = Button(text="Начать измерение", command=start_measurement)
start_measurement.grid(row=3, column=0, columnspan=3, **opts)


root.mainloop()
