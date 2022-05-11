from DataGather.Panels import *
from DataGather.Geosatellite import *
from DataGather.LocationForecast import *
from Prediction.ModelManager import *
from Prediction.Models.RecurrentNN import *
from Prediction.Loaders.ImageDataLoader import *


def gather_data(config_file):
    geosat = Geosatellite(config_file)  # noqa
    # locforecast = LocationForecast(config_file)  # noqa
    panels = Panels(config_file)
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


if __name__ == "__main__":
    config = json.load(open("Config/config.json", "r", encoding="utf-8"))

    # gather_data(config)

    model_manager = ModelManager(RecurrentNN, config["Prediction model parameters"], config["Paths"])
    a = model_manager.train()
