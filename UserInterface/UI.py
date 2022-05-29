from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk

from Controller.Controller import Controller


class UI_Tkinter:
    def __init__(self, config):
        self.config = config
        self.controller = Controller(config)

    def run(self):
        self._init_window()
        self.root.mainloop()

    def _init_window(self):
        self.root = Tk()
        self.root.title("Solar panels energy output forecast")
        self.root.geometry("1000x500")
        self.mainframe = ttk.Frame(self.root, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        # self.mainframe.columnconfigure("all", pad=100)

        style = ttk.Style()
        style.theme_use('alt')
        style.configure('TButton', background='gray', foreground='black', width=20, borderwidth=1, focusthickness=3,
                        focuscolor='none')
        # style.map('TButton', background=[('active', 'red')])

        self.download_button = ttk.Button(self.mainframe, text="Start downloading images",
                                          command=self._download_button_callback, padding="3 3 12 12")
        self.download_button.grid(column=0, row=0, sticky=W, padx=10, pady=10)

        download_stopped_image = Image.open(self.config["Paths"]["GUI_icons"] + "DownloadStopped.png")
        download_stopped_image = download_stopped_image.resize((30, 30))
        self.download_stopped_image = ImageTk.PhotoImage(download_stopped_image)
        download_running_image = Image.open(self.config["Paths"]["GUI_icons"] + "DownloadRunning.png")
        download_running_image = download_running_image.resize((30, 30))
        self.download_running_image = ImageTk.PhotoImage(download_running_image)
        self.download_check_box = ttk.Button(self.mainframe, image=self.download_stopped_image)
        self.download_check_box.state(["disabled"])
        self.download_check_box.grid(column=1, row=0, sticky=W, padx=10, pady=10)

        self.open_db_button = ttk.Button(self.mainframe, text="Open database", padding="3 3 12 12",
                                         command=self._open_db_button_callback)
        self.open_db_button.grid(column=0, row=1, sticky=W, padx=10, pady=10)

        self.refresh_button = ttk.Button(self.mainframe, text="Refresh", padding="3 3 12 12",
                                         command=self._refresh)
        self.refresh_button.grid(column=0, row=2, sticky=W, padx=10, pady=10)

        self.predict_label_title = ttk.Label(self.mainframe, text="Prediction for tomorrow:", padding="100 3 3 3")
        self.predict_label_title.grid(column=3, row=0, sticky=W, pady=10)

        self.cloudy_label = ttk.Label(self.mainframe, text="Cloud percentage:", padding="90 3 3 3")
        self.cloudy_label.grid(column=3, row=1, sticky=W)

        self.actual_prediction_label = ttk.Label(self.mainframe, text=self._get_prediction())  # , padding="3 3 3 3")
        self.actual_prediction_label.grid(column=4, row=1, sticky=W)

        self.power_output_label = ttk.Label(self.mainframe, text="Power output:", padding="90 3 3 3")
        self.power_output_label.grid(column=3, row=2, sticky=W)

        self.actual_power_output = ttk.Label(self.mainframe, text=self._get_power_output())
        self.actual_power_output.grid(column=4, row=2, sticky=W)

    def _download_button_callback(self):
        if self.download_button.config("text")[-1] == "Start downloading images":
            self.controller.start_download_data()
            self.download_button.config(text="Stop downloading")
            self.download_check_box.config(image=self.download_running_image)
        else:
            self.controller.stop_download_data()
            self.download_button.config(text="Start downloading images")
            self.download_check_box.config(image=self.download_stopped_image)

    def _open_db_button_callback(self):
        self.controller.start_sqlite_browser()

    def _get_prediction(self):
        try:
            return str(int(100 - self.controller.get_prediction() * 100)) + "%"
        except ValueError:
            return "No pictures downloaded today"

    def _get_power_output(self):
        try:
            sunny_prediction = self.controller.get_prediction()
        except ValueError:
            return "No pictures downloaded today"
        return str(round(self.controller.get_power_output_based_on_prediction(sunny_prediction), 2)) + "W"

    def _refresh(self):
        self.actual_prediction_label.config(text=self._get_prediction())
