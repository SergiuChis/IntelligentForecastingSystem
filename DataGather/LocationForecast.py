import requests
import json


class LocationForecast:
    def __init__(self, config):
        self.config = config

    def request_and_save(self, unique_part_for_file_name):
        headers_location_forecast = {
            "User-Agent": self.config["Headers"]["User-Agent"],
            "If-Modified-Since": self.config["Last updates"]["locationforecast"]
        }
        location_forecast = requests.get(self.config["URLs"]["locationforecast"], headers=headers_location_forecast, params=self.config["Cluj coordinates"], timeout=5)
        if location_forecast.status_code == 200:
            self.config["Last updates"]["locationforecast"] = location_forecast.headers["Last-Modified"]
            config_file = open("../Config/config.json", "w", encoding="utf-8")
            json.dump(self.config, config_file, indent=4)
            config_file.close()
            output = open("Saves/locationforecast/locationforecast_header_" + unique_part_for_file_name + ".json", "w")
            output.write(str(location_forecast.headers))
            output.close()
            output = open("Saves/locationforecast/locationforecast_body_" + unique_part_for_file_name + ".json", "w")
            json.dump(location_forecast.json(), output)
            output.close()

        print("Loc forecast:", location_forecast.status_code)
        return location_forecast.status_code
