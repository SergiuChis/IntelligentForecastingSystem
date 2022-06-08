from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import os
import json
import sys

from RecommendationsRepo import RecommendationsRepo


class UI_Recommendations:
    def __init__(self, config):
        self.config = config
        self.recommendations_repo = RecommendationsRepo(config)
        self.power_prediction = float(sys.argv[1])

    def run(self):
        self._init_window()
        self.root.mainloop()

    def _init_window(self):
        self.root = Tk()
        self.root.title("Recommendations")
        self.root.geometry("1100x1000")
        self.mainframe = ttk.Frame(self.root, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        # self.mainframe.columnconfigure("all", pad=100)

        style = ttk.Style()
        style.theme_use('alt')
        style.configure('TButton', background='gray', foreground='black', width=20, borderwidth=1, focusthickness=3,
                        focuscolor='none')
        # style.map('TButton', background=[('active', 'red')])

        self.listbox_label = ttk.Label(self.mainframe, text="Activity, power needed")
        self.listbox_label.grid(column=0, row=0)

        self.listbox = Listbox(self.mainframe)
        self.listbox.grid(column=0, row=1, sticky="nsew")

        activity_list = self.recommendations_repo.get_activities_for_specified_power(self.power_prediction)
        index = 1
        for activity in activity_list:
            self.listbox.insert(index, activity[0] + " -> " + str(activity[1]))
            index += 1

        self.all_listbox = Listbox(self.mainframe, width=30)
        self.all_listbox.grid(column=1, row=1)

        index = 1
        for activity in self.recommendations_repo.get_all():
            self.all_listbox.insert(index, activity[0] + " -> " + str(activity[1]))
            index += 1

        self.delete_second_button = ttk.Button(self.mainframe, text="Delete selected", command=self.delete_selected_from_all)
        self.delete_second_button.grid(column=1, row=2)

        self.delete_button = ttk.Button(self.mainframe, text="Delete selected", command=self.delete_selected_activities)
        self.delete_button.grid(column=0, row=2)

        self.refresh_button = ttk.Button(self.mainframe, text="Refresh list", command=self.refresh)
        self.refresh_button.grid(column=0, row=3)

        self.user_input_activity_label = ttk.Label(self.mainframe, text="Input new activity", padding="3 50 3 3")
        self.user_input_activity_label.grid(column=0, row=4)

        self.activity_input_label = ttk.Label(self.mainframe, text="Activity")
        self.activity_input_label.grid(column=0, row=5)

        self.activity_input_textbox = Text(self.mainframe, height=1.5, width=30)
        self.activity_input_textbox.grid(column=0, row=6)

        self.power_input_label = ttk.Label(self.mainframe, text="Power needed")
        self.power_input_label.grid(column=0, row=7)

        self.power_input_textbox = Text(self.mainframe, height=1.5, width=30)
        self.power_input_textbox.grid(column=0, row=8)

        self.insert_button = ttk.Button(self.mainframe, text="Insert activity", padding="3 3 12 12", command=self.insert_activity)
        self.insert_button.grid(column=0, row=9)

    def refresh(self):
        self.listbox.delete(0, self.listbox.size() - 1)
        activity_list = self.recommendations_repo.get_activities_for_specified_power(self.power_prediction)
        index = 1
        for activity in activity_list:
            self.listbox.insert(index, activity[0] + " -> " + str(activity[1]))
            index += 1

        self.all_listbox.delete(0, self.all_listbox.size() - 1)
        activity_list = self.recommendations_repo.get_all()
        index = 1
        for activity in activity_list:
            self.all_listbox.insert(index, activity[0] + " -> " + str(activity[1]))
            index += 1

    def delete_selected_activities(self):
        for index in self.listbox.curselection():
            self.recommendations_repo.delete(self.listbox.get(index).split(" -> ")[0])
        self.refresh()

    def delete_selected_from_all(self):
        for index in self.all_listbox.curselection():
            self.recommendations_repo.delete(self.all_listbox.get(index).split(" -> ")[0])
        self.refresh()

    def insert_activity(self):
        activity = self.activity_input_textbox.get(1.0, "end-1c")
        power = float(self.power_input_textbox.get(1.0, "end-1c"))
        self.recommendations_repo.insert_activity(activity, power)
        self.refresh()


if __name__ == "__main__":
    config = json.load(open("Config/config.json", "r", encoding="utf-8"))
    ui = UI_Recommendations(config)
    ui.run()
