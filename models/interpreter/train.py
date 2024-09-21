import torch
import torch.nn as nn
from config.config import CONFIG

from dataloader import dataloader, data
from model import PoseModel
from loss import PoseLoss

from util.path_resolver import PATH_RESOLVER as REPATH

device = 'cuda' if torch.cuda.is_available() else 'cpu'


def train_model(net, data_loader, optimizer, criterion, num_epochs):
    net.train()

    losses = []
    for epoch in range(num_epochs):
        running_loss = 0.0
        for word_inputs, true_poses, true_eos in data_loader:
            word_inputs = word_inputs.to(device)
            true_poses = true_poses.to(device)
            true_eos = true_eos.to(device)

            # Forward pass
            optimizer.zero_grad()
            predicted_poses, eos_predictions = net(word_inputs)

            # Compute loss
            loss = criterion(predicted_poses, true_poses, eos_predictions, true_eos)

            # Backward pass and optimization
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        running_loss = running_loss / len(dataloader)
        if len(losses) > 1 and running_loss < losses[-1]:
            torch.save({
                'epoch': epoch,
                'model_state_dict': net.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'loss': running_loss,
            }, REPATH.INTERPRETER_DIR / 'checkpoint.pth')
        losses.append(running_loss)

        print(f"Epoch [{epoch + 1}/{num_epochs}], Loss: {running_loss}")


def train_interpreter():
    vocab_size = len(data['word'])
    embedding_dim = 256
    hidden_dim = 128
    num_layers = 1
    output_dim = 147

    model = PoseModel(vocab_size, embedding_dim, hidden_dim, num_layers, output_dim).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = PoseLoss()
    num_epochs = 10

    train_model(model, dataloader, optimizer, criterion, num_epochs)


if __name__ == "__main__":
    train_interpreter()
