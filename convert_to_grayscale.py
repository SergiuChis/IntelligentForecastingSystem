from PIL import Image
import os
import json

config = json.load(open("Config/config.json", "r", encoding="utf-8"))
crops = config["Image crop"]["Romania"]
for image in os.listdir("Saves/geosatellite/new_geosat_after_panels"):

    if image.split(".")[-1] == "png":
        img = Image.open("Saves/geosatellite/new_geosat_after_panels/" + image)
        print((crops["x_upper_left"], crops["y_upper_left"], crops["x_lower_right"], crops["y_lower_right"]))
        img = img.crop((crops["x_upper_left"], crops["y_upper_left"], crops["x_lower_right"], crops["y_lower_right"]))
        # print(img.convert("L").size)
        # break
        img.convert("L").save("Saves/geosatellite/grayscale_images/" + image)
        print("Saved:", image, "as grayscale")
