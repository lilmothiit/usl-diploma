from numpy.random import shuffle

import pickle
import torch
import torch.nn.utils.rnn as rnn_utils
from torch.utils.data import DataLoader, Dataset, SubsetRandomSampler

from util.path_resolver import PATH_RESOLVER as REPATH


data = pickle.load(open(REPATH.POSE_DATA_DIR / 'full_pose_dataset.pkl', 'rb'))

idx_to_word = {}
vocab = {}
for i, word in enumerate(data['word']):
    idx_to_word[i] = word
    vocab[word] = i


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
train_dataloader = DataLoader(dataset, batch_size=32, shuffle=True, collate_fn=collate_fn)


def generate_valid_sample():
    indices = list(range(len(dataset)))
    shuffle(indices)
    val_slice = indices[:int(len(dataset)*0.1)]
    sampler = SubsetRandomSampler(val_slice)
    valid_dataloader = DataLoader(dataset, batch_size=32, sampler=sampler, collate_fn=collate_fn)
    return valid_dataloader
