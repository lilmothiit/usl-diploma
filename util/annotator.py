import bz2
import csv

from util.global_logger import GLOBAL_LOGGER as LOG


class Annotator:
    DEFAULT_HEADER = ['word', 'part_of_speech', 'category', 'site_path', 'local_path']

    def __init__(self, file_path, header=None, delimiter=';'):
        if header is None:
            header = self.DEFAULT_HEADER

        self.file_path = file_path
        self.csv_file = open(self.file_path, 'a', newline='', encoding='utf-8')
        self.writer = csv.writer(self.csv_file, delimiter=delimiter)

        # if the opened file is empty, write the header row
        with open(self.file_path, 'r', encoding='utf-8') as file_obj:
            if not file_obj.read(1):
                self.writer.writerow(header)

    def record(self, line=None, word=None, part_of_speech=None, category=None, site_path=None, local_path=None):
        if line:
            if isinstance(line, (list, tuple)):
                self.writer.writerow(line)
            elif isinstance(line, str):
                self.writer.writerow([line])
            else:
                LOG.error(f"Annotation line must be a list, tuple, or string. Got {type(line)}")

        else:
            if (word, part_of_speech, category, site_path, local_path) == (None, None, None, None, None):
                LOG.error("Annotator cannot record a row if all values are None")
                return
            self.writer.writerow([word, part_of_speech, category, site_path, local_path])

    def __del__(self):
        if hasattr(self, 'csv_file'):
            self.csv_file.close()
