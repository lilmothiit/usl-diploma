import json
import pickle
from io import StringIO
import pandas as pd

from util.path_resolver import PATH_RESOLVER as REPATH
from util.global_logger import GLOBAL_LOGGER as LOG
from config.config import CONFIG

from pathlib import Path


class PoseScribe:
    @staticmethod
    def _json_writer(data, path):
        with open(path, 'w') as f:
            json.dump(data, f, indent='\t')

    @staticmethod
    def _json_reader(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError as e:
            LOG.error(e)
            return None

    @staticmethod
    def _json_pickle_writer(data, path):
        with open(path, 'wb') as f:
            pickle.dump(data, f)

    @staticmethod
    def _json_pickle_reader(path):
        try:
            with open(path, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError as e:
            LOG.error(e)
            return None

    @staticmethod
    def _csv_writer(data, path):
        if isinstance(data, list) and isinstance(data[0], dict):
            try:
                data = pd.json_normalize(data)
            except ValueError as e:
                LOG.error(e)
                return
        else:
            try:
                data = pd.DataFrame(data)
            except ValueError as e:
                LOG.error(e)
                return
        data.to_csv(path, index=False)

    @staticmethod
    def _csv_reader(path):
        try:
            return pd.read_csv(path)
        except ValueError as e:
            LOG.error(e)
            return None

    @staticmethod
    def _csv_pickle_writer(data, path):
        csv_buffer = StringIO()
        if isinstance(data, list):
            if isinstance(data[0], dict):
                data = pd.json_normalize(data)
            else:
                try:
                    data = pd.DataFrame(data)
                except ValueError as e:
                    LOG.error(e)
                    return None

        data.to_csv(csv_buffer, index=False)
        with open(path, 'wb') as f:
            pickle.dump(csv_buffer, f)

    @staticmethod
    def _csv_pickle_reader(path):
        try:
            with open(path, 'rb') as f:
                return pickle.load(f)
        except ValueError as e:
            LOG.error(e)
            return None

    writers = {
        '.json': _json_writer,
        '.json.pkl': _json_pickle_writer,
        '.csv': _csv_writer,
        '.csv.pkl': _csv_pickle_writer
    }

    readers = {
        '.json': _json_reader,
        '.json.pkl': _json_pickle_reader,
        '.csv': _csv_reader,
        '.csv.pkl': _csv_pickle_reader,
    }

    def write(self, data, path: Path):
        for file_type, perform_write in CONFIG.POSE_ANNOTATION_TYPES.items():
            if not perform_write:
                continue

            typed_path = path.parent / (path.name + file_type)
            if REPATH.exists(typed_path) and not CONFIG.FORCE_POSE_ANNOTATION:
                LOG.info(f"Pose annotation already exists: {typed_path}")
                continue
            self.writers[file_type](data, typed_path)

    def read(self, path):
        path = Path(path)

        if not REPATH.exists(path):
            LOG.error(f"Pose annotation does not exists: {path}")
            return

        file_type = ''.join(path.suffixes)
        if file_type not in self.readers:
            LOG.error(f"Pose scribe cannot handle file type {file_type}")
            return

        return self.readers[file_type](path)

    @staticmethod
    def all_selected_exist(untyped_path):
        type_existance = []
        for file_type, perform_write in CONFIG.POSE_ANNOTATION_TYPES.items():
            if not perform_write:
                continue
            typed_path = untyped_path.parent / (untyped_path.name + file_type)
            type_existance.append(REPATH.exists(typed_path))
        return all(type_existance)


pose_scribe = PoseScribe()
