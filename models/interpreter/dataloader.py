import torch
import torch.nn.utils.rnn as rnn_utils
from torch.utils.data import DataLoader, Dataset

from pose_estimation.pose_scribe import pose_scribe
from util.path_resolver import PATH_RESOLVER as REPATH


data = pose_scribe.read(REPATH.WORD_POSE_DIR / '000000_full.msgpack.gz')

idx_to_word = {i: word for i, word in enumerate(data['word'])}
vocab = {word: i for i, word in enumerate(data['word'])}


def collate_fn(batch):
    words, poses, lengths = zip(*batch)
    # Convert words to tensor indices (using a vocabulary or a pre-trained embedding lookup)
    word_tensor = torch.tensor([vocab[word] for word in words], dtype=torch.long)
    # Pad the pose sequences to the max length in this batch
    pose_tensor = rnn_utils.pad_sequence([torch.tensor(p) for p in poses], batch_first=True)
    # Length to binary tensor that uses 1 to indicate end-of-sequence
    length_tensor = []
    for length in lengths:
        tensor = torch.zeros(length, dtype=torch.float)  # Initialize with 0
        tensor[-1] = 1  # Set the last element to 1
        length_tensor.append(tensor)
    length_tensor = rnn_utils.pad_sequence(length_tensor, batch_first=True)

    return word_tensor, pose_tensor, length_tensor


class PoseDataset(Dataset):
    def __init__(self, words, poses, lengths):
        self.words = words
        self.poses = poses
        self.length = lengths

    def __len__(self):
        return len(self.words)

    def __getitem__(self, idx):
        return self.words[idx], self.poses[idx], self.length[idx]


dataset = PoseDataset(data['word'], data['pose'], data['length'])
dataloader = DataLoader(dataset, batch_size=32, shuffle=True, collate_fn=collate_fn)

