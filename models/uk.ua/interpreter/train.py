import torch
from dataloader import dataloader, data
from model import PoseModel
from loss import PoseLoss

from config.config import CONFIG
from util.path_resolver import PATH_RESOLVER as REPATH

device = 'cuda' if torch.cuda.is_available() else 'cpu'


def train_interpreter():
    vocab_size = len(data['word'])
    embedding_dim = CONFIG.INTERPRETER_EMBEDDING_DIM
    hidden_dim = CONFIG.INTERPRETER_HIDDEN_DIM
    output_dim = len(data['pose'][0][0])

    model = PoseModel(vocab_size, embedding_dim, hidden_dim, output_dim)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)
    criterion = PoseLoss()
    num_epochs = 20
    load_epoch = 0
    losses = []

    save_path = REPATH.INTERPRETER_DIR / f'{vocab_size}v-{embedding_dim}e-{hidden_dim}h-{output_dim}o'

    if not REPATH.exists(save_path):
        save_path.mkdir(parents=True, exist_ok=True)
    else:
        print(f'Restored model from {save_path}')
        checkpoint = torch.load(save_path / f'checkpoint.pth')

        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        scheduler.load_state_dict(checkpoint['scheduler_state_dict'])

        load_epoch = checkpoint['epoch']
        losses = checkpoint['losses']

    model.to(device)
    for epoch in range(load_epoch, num_epochs):
        running_loss = 0.0
        for word_inputs, true_poses, true_eos in dataloader:
            word_inputs = word_inputs.to(device)
            true_poses = true_poses.to(device)
            true_eos = true_eos.to(device)

            # Forward pass
            optimizer.zero_grad()
            predicted_poses, eos_predictions = model(word_inputs)

            # Compute loss
            loss = criterion(predicted_poses, true_poses, eos_predictions, true_eos)

            # Backward pass and optimization
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        running_loss = running_loss / len(dataloader)
        if len(losses) > 0 and running_loss < min(losses):
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'scheduler_state_dict': scheduler.state_dict(),
                'losses': losses,
            }, save_path / f'checkpoint.pth')
        losses.append(running_loss)

        scheduler.step(running_loss)

        print(f"Epoch [{epoch + 1}/{num_epochs}], Loss: {running_loss}")


if __name__ == "__main__":
    train_interpreter()
