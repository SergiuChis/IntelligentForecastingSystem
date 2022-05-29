from PIL import Image
import numpy as np
from matplotlib import pyplot
import os
import sqlite3
import json


class ImageAnalysis:
    @staticmethod
    def show_array_image(image_as_array):
        pyplot.imshow(image_as_array, cmap="gray")
        pyplot.show()

    @staticmethod
    def crop_matrix(matrix, row_upper_left, col_upper_left, row_lower_right, col_lower_right):
        i_new = 0
        new_arr = np.zeros((row_lower_right - row_upper_left, col_lower_right - col_upper_left))
        for i in range(row_upper_left, row_lower_right):
            j_new = 0
            for j in range(col_upper_left, col_lower_right):
                new_arr[i_new][j_new] = matrix[i][j]
                j_new += 1
            i_new += 1
        return new_arr

    @staticmethod
    def get_only_clouds(image_as_array):
        threshold = 180
        for i in range(len(image_as_array)):
            for j in range(len(image_as_array[i])):
                if image_as_array[i][j] < threshold:
                    image_as_array[i][j] = 0
        return image_as_array

    @staticmethod
    def how_sunny_it_is_over_cluj(image_as_array, crop_coords):
        nr_of_black_pixels = 0
        nr_of_pixels = (crop_coords["x_lower_right"] - crop_coords["x_upper_left"]) * (crop_coords["y_lower_right"] - crop_coords["y_upper_left"])
        cropped_image_as_array = ImageAnalysis.crop_matrix(image_as_array, crop_coords["y_upper_left"], crop_coords["x_upper_left"], crop_coords["y_lower_right"], crop_coords["x_lower_right"])
        for row in cropped_image_as_array:
            for col in row:
                if col == 0:
                    nr_of_black_pixels += 1
        return nr_of_black_pixels / nr_of_pixels

    @staticmethod
    def process_images_for_training():
        config = json.load(open("Config/config.json", "r", encoding="utf-8"))
        crops = config["Image crop"]["Romania"]
        for image in os.listdir("Saves/geosatellite/new_geosat_after_panels"):

            if image.split(".")[-1] == "png":
                img = Image.open("Saves/geosatellite/new_geosat_after_panels/" + image)
                print((crops["x_upper_left"], crops["y_upper_left"], crops["x_lower_right"], crops["y_lower_right"]))
                img = img.crop(
                    (crops["x_upper_left"], crops["y_upper_left"], crops["x_lower_right"], crops["y_lower_right"]))
                # print(img.convert("L").size)
                # break
                img.convert("L").save("Saves/geosatellite/grayscale_images/" + image)
                print("Saved:", image, "as grayscale")


    # if __name__ == "__main__":
    #     i = 0
    #     conn = sqlite3.connect("../Saves/SQL_grouped/data_for_training.sqlite")
    #     for image_file_name in os.listdir("../Saves/geosatellite/new_geosat_after_panels"):
    #         if image_file_name.split(".")[-1] == "png":
    #             image = Image.open("../Saves/geosatellite/new_geosat_after_panels/Europe-IR-20220508173000.png") # + image_file_name)
    #             image = get_only_clouds(np.array(image.convert("L")))  # noqa
    #             Image.fromarray(image, mode="L").show()
    #             break
    #             a = how_sunny_it_is_over_cluj(image)
    #             conn.execute("update images set sunny_value=? where name=?", (a, image_file_name))
    #             print(i)
    #             i += 1
    #     conn.commit()
    #     conn.close()
