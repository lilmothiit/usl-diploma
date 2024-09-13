import json
import gzip
import msgpack

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
        with open(path, 'r') as f:
            return json.load(f)

    @staticmethod
    def _msgpack_gzip_writer(data, path):
        with gzip.open(path, 'wb') as f:
            packed_data = msgpack.packb(data)
            f.write(packed_data)

    @staticmethod
    def _msgpack_gzip_reader(path):
        with gzip.open(path, 'wb') as f:
            return msgpack.unpackb(f.read())

    writers = {
        '.json': _json_writer,
        '.msgpack.gz': _msgpack_gzip_writer
    }

    readers = {
        '.json': _json_reader,
        '.msgpack.gz': _msgpack_gzip_reader
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
