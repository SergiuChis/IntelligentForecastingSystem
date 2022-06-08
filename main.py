import json

from UserInterface.UI import UI_Tkinter
from Prediction.ModelManager import ModelManager
from Prediction.Models.RecurrentNN import RecurrentNN
from Controller.Controller import Controller


if __name__ == "__main__":
    config = json.load(open("Config/config.json", "r", encoding="utf-8"))

    ui = UI_Tkinter(config)
    ui.run()
