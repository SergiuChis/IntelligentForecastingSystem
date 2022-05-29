import os
from PIL import Image
import numpy as np
import sqlite3
import random
from datetime import datetime
from statistics import mean


class ImageDataLoader:
    def __init__(self, image_folder_path, device="cuda", shuffle=False):
        self.device = device
        self.image_folder_path = image_folder_path
        self.images = self.__split_by_days(
            list(filter(lambda element: element.split(".")[-1] == "png", os.listdir(image_folder_path)))
        )
        if shuffle:
            random.shuffle(self.images)
        self.day = 0
        self.img_idx = 0

    def __iter__(self):
        self.day = 0
        self.img_idx = 0
        return self

    def __next__(self):
        # while self.day < len(self.images) and len(self.images[self.day]) - self.img_idx < 20:
        #     self.day += 1
        #     self.img_idx = 0
        # if self.day >= len(self.images):
        #     raise StopIteration
        # ret = self.images[self.day][self.img_idx:self.img_idx + 5], self.images[self.day][self.img_idx + 19]
        # self.img_idx += 1
        # return self.__to_tensor(ret)
        if self.day < len(self.images):
            self.day += 1
            return self.__to_tensor(self.images[self.day - 1])
        raise StopIteration

    def get_dataset_by_date(self, date):
        year = date.tm_year
        month = date.tm_mon
        day = date.tm_mday
        today_as_string = str(year) + "-" + str(month).zfill(2) + "-" + str(day).zfill(2)

        conn = sqlite3.connect("Saves/SQL_grouped/data_for_training.sqlite")
        print("select name from images where date(date)='" + today_as_string + "'")
        today_images = conn.execute("select name from images where date(date)='" + today_as_string + "'")

        sequence = []
        for image in today_images:
            img = Image.open(self.image_folder_path + "/" + image[0])
            gray_scale_img = np.array(img).flatten()
            sequence.append(gray_scale_img)

        if len(sequence) == 0:
            raise ValueError("No images downloaded today")

        return sequence

    def __to_tensor(self, chunk):
        result = ([],)
        for element in chunk[0]:
            image = Image.open(self.image_folder_path + "/" + element)
            gray_scale_image_as_tensor = np.array(image).flatten()
            result[0].append(gray_scale_image_as_tensor)
        conn = sqlite3.connect("Saves/SQL_grouped/data_for_training.sqlite")
        sunny_values = []
        for element in chunk[1]:
            sunny_value = conn.execute("select sunny_value from images where name=?", (element,))
            sunny_values.append(next(sunny_value)[0])
        average = mean(sunny_values)
        result += (average,)
        return result

    @staticmethod
    def __split_by_days(lst):
        days_dict = {}
        for image in lst:
            date = image.split("-")[2].split(".")[0][:8]
            if date in days_dict:
                days_dict[date].append(image)
            else:
                days_dict[date] = [image]
        result = []
        keys = list(days_dict.keys())
        for i in range(len(keys) - 1):
            for j in range(i + 1, len(keys)):
                curr_date = datetime.strptime(keys[i], "%Y%m%d")
                next_date = datetime.strptime(keys[j], "%Y%m%d")
                difference = next_date - curr_date
                if difference.days == 1:
                    result.append([days_dict[keys[i]], days_dict[keys[j]]])

        return result
