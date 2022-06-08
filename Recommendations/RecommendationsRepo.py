import sqlite3
from copy import deepcopy


class RecommendationsRepo:
    def __init__(self, config):
        self.config = config
        self.db_conn = sqlite3.connect(config["Paths"]["recommendations_database"])
        self.db_conn.execute("create table if not exists activities (id integer primary key autoincrement, activity string, power_needed real)")  # noqa
        self._best_combination = []

    def insert_activity(self, activity, power_needed):
        self.db_conn.execute("insert into activities (activity, power_needed) values (?, ?)", (activity, power_needed))
        self.db_conn.commit()

    def get_activities_for_specified_power(self, power):
        activities = self.db_conn.execute("select activity, power_needed from activities")  # noqa
        self._best_combination = []
        self._get_activities_for_specified_power(activities.fetchall(), [], [], power, 0, 0)
        return self._best_combination

    @staticmethod
    def _add_to_list(lst, elem, index):
        try:
            lst[index] = elem
        except:
            lst.append(elem)

    @staticmethod
    def _get_sum(combination):
        sum = 0
        for activity in combination:
            sum += activity[1]
        return sum

    def _get_activities_for_specified_power(self, activities, tries, already_tried, power, index, sum):
        for activity in activities:
            if activity not in already_tried and sum + activity[1] <= power:
                self._add_to_list(tries, activity, index)
                already_tried.append(activity)
                self._get_activities_for_specified_power(activities, tries, already_tried, power, index + 1, sum + activity[1])  # noqa
                already_tried.remove(activity)
        if abs(power - sum) < abs(power - self._get_sum(self._best_combination)):
            self._best_combination = deepcopy(tries)
            del tries[index:]

    def get_all(self):
        activities = self.db_conn.execute("select activity, power_needed from activities")
        return activities.fetchall()

    def delete(self, activity):
        self.db_conn.execute("delete from activities where activity=?", (activity,))
        self.db_conn.commit()
