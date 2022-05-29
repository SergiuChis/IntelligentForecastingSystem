import requests
import json
import sqlite3
from PIL import Image
import numpy as np
from utilities import convert_img_to_binary_data, str_to_datetime
from ImageAnalysis.ImageAnalysis import ImageAnalysis


class Geosatellite:
    def __init__(self, config):
        self.config = config
        self.db_conn = sqlite3.connect(config["Paths"]["database"])

    def request_and_save(self):
        image_id = -1
        headers_geosatellite = {
            "User-Agent": self.config["Headers"]["User-Agent"],
            "If-Modified-Since": self.config["Last updates"]["geosatellite"]
        }
        geosatellite = requests.get(self.config["URLs"]["geosatellite"], headers=headers_geosatellite, timeout=5)
        if geosatellite.status_code == 200:
            self.config["Last updates"]["geosatellite"] = geosatellite.headers["Last-Modified"]
            config_file = open("Config/config.json", "w", encoding="utf-8")
            json.dump(self.config, config_file, indent=4)
            config_file.close()
            image_name = geosatellite.headers["Content-Type"].split("\"")[1].split(".")[0]
            headers = open("Saves/geosatellite/new_geosat_after_panels/" + image_name + ".json", "w", encoding="utf-8")
            headers.write(str(geosatellite.headers))
            headers.close()
            img = open("Saves/geosatellite/new_geosat_after_panels/" + image_name + ".png", "wb")
            for chunk in geosatellite:
                img.write(chunk)
            img.close()

            timestamp = str_to_datetime(image_name.split("-")[-1].split(".")[0])
            blob_picture = convert_img_to_binary_data("Saves/geosatellite/new_geosat_after_panels/" + image_name + ".png")
            image = Image.open("Saves/geosatellite/new_geosat_after_panels/" + image_name + ".png")
            image = ImageAnalysis.get_only_clouds(np.array(image.convert("L")))
            sunny_value = ImageAnalysis.how_sunny_it_is_over_cluj(image, self.config["Image crop"]["Cluj"])
            print("Inserting into images values:", image_name + ".png", "blob", timestamp, sunny_value)
            cursor = self.db_conn.execute("insert into images (name, photo, date, sunny_value) values (?, ?, ?, ?)", (image_name + ".png", blob_picture, timestamp, sunny_value))
            self.db_conn.commit()
            image_id = cursor.lastrowid

        print("Geosat:", geosatellite.status_code)
        return geosatellite.status_code, image_id
