import os
import csv


class Annotator:
    DEFAULT_HEADER = ['word', 'part_of_speech', 'category', 'site_path', 'local_path']

    def __init__(self, file_path, header=None):
        if header is None:
            header = self.DEFAULT_HEADER

        self.file_path = file_path
        self.csv_file = open(self.file_path, 'a', newline='', encoding='utf-8')
        self.writer = csv.writer(self.csv_file, delimiter=';')

        if not os.path.exists(self.file_path):
            self.writer.writerow(header)

    def record(self, line=None, word=None, part_of_speech=None, category=None, site_path=None, local_path=None):
        if line:
            if isinstance(line, (list, tuple)):
                self.writer.writerow(line)
            elif isinstance(line, str):
                self.writer.writerow([line])
            else:
                raise ValueError("Line must be a list, tuple, or string")

        else:
            if (word, part_of_speech, category, site_path, local_path) == (None, None, None, None, None):
                raise ValueError("Cannot record a row if all values are None")
            self.writer.writerow([word, part_of_speech, category, site_path, local_path])

    def __del__(self):
        if self.csv_file:
            self.csv_file.close()
