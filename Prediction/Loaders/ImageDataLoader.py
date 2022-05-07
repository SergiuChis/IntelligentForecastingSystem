import os
from torchvision import transforms
from PIL import Image
import random
import torch
from DataGather.image_analysis import get_only_clouds
import numpy as np
import sqlite3
import random


class ImageDataLoader:
    def __init__(self, image_folder_path, device="cuda", shuffle=False):
        self.device = device
        self.image_folder_path = image_folder_path
        _, self.images = self.__split_by_days(
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
        while self.day < len(self.images) and len(self.images[self.day]) - self.img_idx < 10:
            self.day += 1
            self.img_idx = 0
        if self.day >= len(self.images):
            raise StopIteration
        ret = self.images[self.day][self.img_idx:self.img_idx + 9], self.images[self.day][self.img_idx + 9]
        self.img_idx += 1
        return self.__to_tensor(ret)

    def __to_tensor(self, chunk):
        result = ([],)
        # transform = transforms.PILToTensor()
        for element in chunk[0]:
            image = Image.open(self.image_folder_path + "/" + element)
            # gray_scale_image_as_tensor = torch.flatten(torch.tensor(np.array(image)).to(self.device))
            gray_scale_image_as_tensor = np.array(image).flatten()
            result[0].append(gray_scale_image_as_tensor)
        # image = Image.open(self.image_folder_path + "/" + chunk[1])
        # gray_scale_image_as_tensor = torch.flatten(torch.tensor(np.array(image)).to(self.device))
        conn = sqlite3.connect("Saves/SQL_grouped/data_for_training.sqlite")
        a = conn.execute("select sunny_value from images where name=?", (chunk[1],))
        # result += (torch.tensor([next(a)[0]]).to(self.device),)
        # result += (np.array(image).flatten(),)
        result += (next(a)[0],)
        return result

    @staticmethod
    def __split_by_days(lst):
        result = {}
        for image in lst:
            date = image.split("-")[2].split(".")[0][:8]
            if date in result:
                result[date].append(image)
            else:
                result[date] = [image]
        return list(result.keys()), list(result.values())
