import os
import sqlite3
from datetime import datetime


CREATE_TABLE_IMAGES = "create table if not exists images (id int primary key, name text not null, photo blob not null, date timestamp not null)"  # noqa
CREATE_TABLE_CURRENT_RECORDS = "create table if not exists current (id int primary key, value real not null, date timestamp not null, image_id int, foreign key(image_id) references images(id))"  # noqa
CREATE_TABLE_VOLTAGE_RECORDS = "create table if not exists voltage (id int primary key, value real not null, date timestamp not null, image_id int, foreign key(image_id) references images(id))"  # noqa


def convert_img_to_binary_data(image_path):
    image_descriptor = open(image_path, "rb")
    blob_data = image_descriptor.read()
    image_descriptor.close()
    return blob_data


def str_to_datetime(date_str):
    year = date_str[0:4]
    month = date_str[4:6]
    day = date_str[6:8]
    hour = date_str[8:10]
    minute = date_str[10:12]
    second = date_str[12:14]
    return datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))


def date_difference(date1, date2):
    diff = abs(date1 - date2)
    seconds_in_day = 24 * 60 * 60
    return diff.days * seconds_in_day + diff.seconds


def keep_only_png(images_list):
    result = []
    for image in images_list:
        if image.split(".")[-1] == "png":
            result.append(image)
    return result


def group_images_with_panel_records(images_directory_path, panels_current_file_path, panels_voltage_file_path, output_database_path):  # noqa
    images_directory_path.strip("/")
    output_database_path.strip("/")

    output_connection_sqlite = sqlite3.connect(output_database_path)
    output_connection_sqlite.execute(CREATE_TABLE_IMAGES)
    output_connection_sqlite.execute(CREATE_TABLE_CURRENT_RECORDS)
    output_connection_sqlite.execute(CREATE_TABLE_VOLTAGE_RECORDS)

    panels_current_file_descriptor = open(panels_current_file_path, "r", encoding="utf-8")
    next(panels_current_file_descriptor)  # hopping over the header
    panels_voltage_file_descriptor = open(panels_voltage_file_path, "r", encoding="utf-8")
    next(panels_voltage_file_descriptor)  # hopping over the header

    images_dir_content = os.listdir(images_directory_path)
    images = keep_only_png(images_dir_content)
    image_id = 0
    for image_name in images:
        timestamp = str_to_datetime(image_name.split("-")[-1].split(".")[0])
        binary_data = convert_img_to_binary_data(images_directory_path + "/" + image_name)
        output_connection_sqlite.execute("insert into images values (?, ?, ?, ?)", (image_id, image_name, binary_data, timestamp))  # noqa
        image_id += 1

    current_id = 0
    for current_record in panels_current_file_descriptor:
        current_record.strip()
        record_split = current_record.split("\t")
        value = record_split[0]
        current_timestamp = str_to_datetime(record_split[1])

        closest_distance = 999999999999
        image_id = 0
        current_record_to_add = None
        for image_name in images:
            img_timestamp = str_to_datetime(image_name.split("-")[-1].split(".")[0])
            difference_in_seconds = date_difference(current_timestamp, img_timestamp)
            if difference_in_seconds < closest_distance:
                closest_distance = difference_in_seconds
                current_record_to_add = (current_id, value, current_timestamp, image_id)
            image_id += 1
        output_connection_sqlite.execute("insert into current values (?, ?, ?, ?)", current_record_to_add)
        current_id += 1

    voltage_id = 0
    for voltage_record in panels_voltage_file_descriptor:
        voltage_record.strip()
        record_split = voltage_record.split("\t")
        value = record_split[0]
        voltage_timestamp = str_to_datetime(record_split[1])

        closest_distance = 999999999999
        image_id = 0
        voltage_record_to_add = None
        for image_name in images:
            img_timestamp = str_to_datetime(image_name.split("-")[-1].split(".")[0])
            difference_in_seconds = date_difference(voltage_timestamp, img_timestamp)
            if difference_in_seconds < closest_distance:
                closest_distance = difference_in_seconds
                voltage_record_to_add = (voltage_id, value, voltage_timestamp, image_id)
            image_id += 1
        output_connection_sqlite.execute("insert into voltage values (?, ?, ?, ?)", voltage_record_to_add)
        voltage_id += 1

    panels_current_file_descriptor.close()
    panels_voltage_file_descriptor.close()
    output_connection_sqlite.commit()
    output_connection_sqlite.close()
