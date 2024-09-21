import torch
import torch.nn as nn


class PoseModel(nn.Module):
    def __init__(self, vocab_size, embedding_dim, hidden_dim, num_layers, output_dim):
        super(PoseModel, self).__init__()

        self.hidden_dim = hidden_dim

        # Word embedding layer
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        # RNN to generate sequence of poses
        self.rnn = nn.LSTM(embedding_dim, hidden_dim, num_layers, batch_first=True)
        # FC layer to map hidden states to coordinates
        self.fc = nn.Linear(hidden_dim, output_dim)
        # FC layer to predict end-of-sequence
        self.eos_classifier = nn.Linear(hidden_dim, 1)  # Binary output: 0 or 1 (continue or stop)

    def forward(self, word_input, max_seq_len=350):
        embedded = self.embedding(word_input)  # (batch_size, embedding_dim)

        # Initialize hidden states
        batch_size = word_input.size(0)
        h_0 = torch.zeros(1, batch_size, self.hidden_dim).to(word_input.device)
        c_0 = torch.zeros(1, batch_size, self.hidden_dim).to(word_input.device)

        # Use RNN to generate sequence of poses
        outputs = []
        eos_predictions = []
        input_seq = embedded.unsqueeze(1)  # Add sequence dimension (batch_size, 1, embedding_dim)

        for t in range(max_seq_len):
            rnn_out, (h_0, c_0) = self.rnn(input_seq, (h_0, c_0))  # (batch_size, 1, hidden_dim)
            pose_out = self.fc(rnn_out.squeeze(1))  # Predict (x, y, z) coordinates

            # Predict whether to stop the sequence (EOS token)
            eos_out = torch.sigmoid(self.eos_classifier(rnn_out.squeeze(1)))

            outputs.append(pose_out)
            eos_predictions.append(eos_out)

            # Check if all batches have predicted EOS
            if torch.all(eos_out > 0.5):  # Assume 0.5 threshold for EOS token
                break

            # Prepare the input for the next timestep (use current output as next input)
            input_seq = embedded.unsqueeze(1)

        # Stack the outputs to form the sequence of poses
        outputs = torch.stack(outputs, dim=1)  # (batch_size, seq_len, 147)
        eos_predictions = torch.stack(eos_predictions, dim=1)  # (batch_size, seq_len, 1)

        return outputs, eos_predictions
