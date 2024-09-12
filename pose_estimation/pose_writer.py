import gzip
import msgpack


class PoseWriter:
    @staticmethod
    def write(data, path):
        with gzip.open(path, 'wb') as f:
            packed_data = msgpack.packb(data)
            f.write(packed_data)

    @staticmethod
    def read(path):
        with gzip.open(path, 'rb') as f:
            loaded_data = msgpack.unpackb(f.read())
            return loaded_data


POSE_WRITER = PoseWriter()
