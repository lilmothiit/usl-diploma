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
            csv_buffer.seek(0)
            pickle.dump(csv_buffer, f)

    @staticmethod
    def _csv_pickle_reader(path):
        try:
            with open(path, 'rb') as f:
                csv_buffer = pickle.load(f)
            csv_buffer.seek(0)
            return pd.read_csv(csv_buffer)
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
        for file_type, perform_write in CONFIG.POSE_ANNOTATION_FILE_TYPES.items():
            if not perform_write:
                continue

            typed_path = path.parent / (path.name + file_type)
            if REPATH.exists(typed_path) and not CONFIG.FORCE_POSE_ANNOTATION:
                LOG.info(f"Pose annotation already exists: {typed_path}")
                continue
            self.writers[file_type](data, typed_path)

    def read(self, path):
        def _typed_read(t_path, f_type=None):
            if not REPATH.exists(t_path):
                LOG.error(f"Pose annotation does not exists: {t_path}")
                return

            if f_type is None:
                f_type = ''.join(t_path.suffixes)
            if f_type not in self.readers:
                LOG.error(f"Pose scribe cannot handle file type {f_type}")
                return

            return self.readers[f_type](path)

        path = Path(path)
        if not path.suffixes:
            files_dict = {}
            for file_type, perform_read in CONFIG.POSE_ANNOTATION_FILE_TYPES.items():
                if not perform_read:
                    continue
                typed_path = path.parent / (path.name + file_type)
                files_dict[file_type] = _typed_read(typed_path, file_type)
            return files_dict
        else:
            return _typed_read(path)

    @staticmethod
    def all_selected_types_exist(path):
        type_existence = []
        for file_type, perform_write in CONFIG.POSE_ANNOTATION_FILE_TYPES.items():
            if not perform_write:
                continue
            typed_path = path.parent / (path.name + file_type)
            type_existence.append(REPATH.exists(typed_path))
        return all(type_existence)


pose_scribe = PoseScribe()
