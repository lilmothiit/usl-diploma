import torch
from dataloader import train_dataloader, data, generate_valid_sample
from model import PoseModel
from loss import PoseLoss

from config.config import CONFIG
from util.path_resolver import PATH_RESOLVER as REPATH
from util.global_logger import GLOBAL_LOGGER as LOG

device = 'cuda' if torch.cuda.is_available() else 'cpu'


class EarlyStopper:
    def __init__(self, patience=5, min_delta=0.001):
        self.patience = patience
        self.min_delta = min_delta
        self.best_loss = None
        self.counter = 0

    def should_stop(self, val_loss):
        if self.best_loss is None or val_loss < self.best_loss - self.min_delta:
            self.best_loss = val_loss
            self.counter = 0
        else:
            self.counter += 1
        return self.counter >= self.patience


def train_interpreter():
    LOG.info('Starting training for interpreter.')

    vocab_size = len(data['word'])
    embedding_dim = CONFIG.INTERPRETER_EMBEDDING_DIM
    hidden_dim = CONFIG.INTERPRETER_HIDDEN_DIM
    output_dim = len(data['pose'][0][0])

    LOG.info(f'vocab_size: {vocab_size}, embedding_dim: {embedding_dim}, '
             f'hidden_dim: {hidden_dim}, output_dim: {output_dim}')

    model = PoseModel(vocab_size, embedding_dim, hidden_dim, output_dim)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)
    criterion = PoseLoss()
    num_epochs = 30
    load_epoch = 0
    train_losses = []
    valid_losses = []

    early_stopper = EarlyStopper(patience=5, min_delta=0.001)

    save_path = REPATH.INTERPRETER_DIR / f'{vocab_size}v-{embedding_dim}e-{hidden_dim}h-{output_dim}o'

    if not REPATH.exists(save_path):
        save_path.mkdir(parents=True, exist_ok=True)
    if REPATH.exists(save_path / 'checkpoint.pth'):
        checkpoint = torch.load(save_path / f'checkpoint.pth')

        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        scheduler.load_state_dict(checkpoint['scheduler_state_dict'])

        load_epoch = checkpoint['epoch']
        train_losses = checkpoint['train_losses']
        valid_losses = checkpoint['valid_losses']

        LOG.info(f'Restored model from {save_path}. Epoch: {load_epoch}')

    model.to(device)

    def epoch_step(word_inputs, true_poses, true_eos):
        word_inputs = word_inputs.to(device)
        true_poses = true_poses.to(device)
        true_eos = true_eos.to(device)

        # Forward pass
        optimizer.zero_grad()
        predicted_poses, eos_predictions = model(word_inputs)

        # Compute loss
        loss = criterion(predicted_poses, true_poses, eos_predictions, true_eos)
        return loss

    def train():
        model.train()
        train_loss = 0.0
        for word_inputs, true_poses, true_eos in train_dataloader:
            loss = epoch_step(word_inputs, true_poses, true_eos)

            # Backward pass and optimization
            loss.backward()
            optimizer.step()

            train_loss += loss.item()

        return train_loss / len(train_dataloader)

    def valid():
        model.eval()
        valid_loss = 0.0
        valid_dataloader = generate_valid_sample()
        for word_inputs, true_poses, true_eos in valid_dataloader:
            loss = epoch_step(word_inputs, true_poses, true_eos)
            valid_loss += loss.item()

        return valid_loss / len(valid_dataloader)

    for epoch in range(load_epoch, num_epochs):
        train_loss = train()
        valid_loss = valid()

        LOG.info(f"Epoch [{epoch + 1}/{num_epochs}], Train Loss: {train_loss}, Validation Loss: {valid_loss}")

        if len(valid_losses) > 0 and valid_loss < min(valid_losses):
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'scheduler_state_dict': scheduler.state_dict(),
                'train_losses': train_losses,
                'valid_losses': valid_losses
            }, save_path / f'checkpoint.pth')

        train_losses.append(train_loss)
        valid_losses.append(valid_loss)

        scheduler.step(train_loss)
        current_lr = optimizer.param_groups[0]['lr']

        if current_lr < 1e-6:
            LOG.info(f"Learning rate too small: {current_lr} < 1e-6.")
            LOG.info(f"Stopping training at epoch [{epoch + 1}/{num_epochs}]")
            break

        if early_stopper.should_stop(valid_loss):
            LOG.info(f"Validation loss has not progressed for the last {early_stopper.patience} epochs.")
            LOG.info(f"Stopping training at epoch [{epoch + 1}/{num_epochs}]")
            break


if __name__ == "__main__":
    train_interpreter()
