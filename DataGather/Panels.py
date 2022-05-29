from selenium import webdriver
import time
import sqlite3
from utilities import str_to_datetime


class Panels:
    def __init__(self, config):
        self.config = config
        self.driver = webdriver.Firefox()
        self.driver.minimize_window()
        self.driver.get(config["URLs"]["panels"])
        self.current_dc = self.driver.find_elements(by="xpath", value="/html/body/div[3]/ni-front-panel/jqx-numeric-text-box[1]")  # noqa
        self.voltage_dc = self.driver.find_elements(by="xpath", value="/html/body/div[3]/ni-front-panel/jqx-numeric-text-box[2]")  # noqa
        self.db_conn = sqlite3.connect(self.config["Paths"]["database"])

    def get_current_dc(self):
        return float(self.current_dc[0].get_attribute("value"))

    def get_voltage_dc(self):
        return float(self.voltage_dc[0].get_attribute("value"))

    def request_and_save(self, image_id):
        current_gmt_time = time.strftime("%G%m%d%H%M%S", time.gmtime())
        current_dc_value = self.get_current_dc()
        voltage_dc_value = self.get_voltage_dc()

        current_dc_file = open("Saves/panels/current_dc.tsv", "a", encoding="utf-8")
        voltage_dc_file = open("Saves/panels/voltage_dc.tsv", "a", encoding="utf-8")

        self.db_conn.execute("insert into current (value, date, image_id) values (?, ?, ?)", (current_dc_value, str_to_datetime(current_gmt_time), image_id))  # noqa
        self.db_conn.execute("insert into voltage (value, date, image_id) values (?, ?, ?)", (voltage_dc_value, str_to_datetime(current_gmt_time), image_id))  # noqa
        self.db_conn.commit()
        current_dc_file.write(str(current_dc_value) + "\t" + current_gmt_time + "\n")
        voltage_dc_file.write(str(voltage_dc_value) + "\t" + current_gmt_time + "\n")

        current_dc_file.close()
        voltage_dc_file.close()

    def close_browser(self):
        self.driver.quit()
