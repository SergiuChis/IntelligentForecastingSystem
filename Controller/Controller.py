import time
import signal
import sys
import subprocess
from multiprocessing import Process
import sqlite3

from DataGather.Panels import Panels
from DataGather.Geosatellite import Geosatellite
from Prediction.ModelManager import ModelManager
from Prediction.Models.RecurrentNN import RecurrentNN
from ImageAnalysis.ImageAnalysis import ImageAnalysis


class Controller:
    def __init__(self, config):
        self.config = config
        self.download_process = Process(target=self._gather_data_process)
        self.db_browser_process = Process(target=self._db_browser_process)
        self.prediction_model_manager = ModelManager(RecurrentNN, config["Prediction model parameters"], config["Paths"])

    def start_download_data(self):
        print("Starting download...")
        try:
            self.download_process.start()
        except AssertionError:
            self.download_process = Process(target=self._gather_data_process)
            self.download_process.start()

    def stop_download_data(self):
        print("Stopping download...")
        self.download_process.terminate()

    def start_sqlite_browser(self):
        print("Starting sqlite browser...")
        try:
            self.db_browser_process.start()
        except AssertionError:
            self.db_browser_process = Process(target=self._db_browser_process)
            self.db_browser_process.start()

    def _db_browser_process(self):
        subprocess.run([self.config["SqliteBrowser_BinaryName"], self.config["Paths"]["database"]])

    def _gather_data_process(self):
        geosat = Geosatellite(self.config)  # noqa
        # locforecast = LocationForecast(config_file)  # noqa
        panels = Panels(self.config)

        def sigterm_handler(sig, frame):
            panels.close_browser()
            sys.exit(0)

        signal.signal(signal.SIGTERM, sigterm_handler)
        time.sleep(20)

        image_id = -1
        while True:
            geosat_status_code, tmp_image_id = geosat.request_and_save()  # noqa
            if tmp_image_id > image_id:
                image_id = tmp_image_id

            for i in range(30):
                panels.request_and_save(image_id)
                sleep_time_secs = 10
                time.sleep(sleep_time_secs)

    def get_prediction(self):
        self.prediction_model_manager.load_saved_model(self.config["Paths"]["trained_model"])
        try:
            return self.prediction_model_manager.predict()[0].item()
        except FileNotFoundError:
            ImageAnalysis.process_images_for_training()
            return self.prediction_model_manager.predict()[0].item()

    def get_power_output_based_on_prediction(self, prediction):
        conn = sqlite3.connect(self.config["Paths"]["database"])
        closest_image_sunny_value_cursor = conn.execute("select id from images order by ABS(? - sunny_value) limit 1", (prediction,))

        image_id = next(closest_image_sunny_value_cursor)[0]
        print("Image id", image_id)

        current_values = conn.execute("select value from current where image_id=?", (image_id,))
        voltage_values = conn.execute("select value from voltage where image_id=?", (image_id,))

        current_list = []
        for current_value in current_values:
            current_list.append(current_value[0])
        voltage_list = []
        for voltage_value in voltage_values:
            voltage_list.append(voltage_value[0])

        conn.close()

        return (sum(current_list)/len(current_list)) * (sum(voltage_list)/len(voltage_list))
