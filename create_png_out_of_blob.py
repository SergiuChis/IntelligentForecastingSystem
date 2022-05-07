import sqlite3
import sys


if __name__ == "__main__":
    output_file = open(sys.argv[2], "wb")
    conn = sqlite3.connect("Saves/SQL_grouped/data_for_training.sqlite")
    cursor = conn.execute("select photo from images where id=" + sys.argv[1])
    blob = cursor.fetchone()
    output_file.write(blob[0])
    cursor.close()
    conn.close()
