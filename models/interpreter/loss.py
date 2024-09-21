import torch.nn as nn
import torch.nn.functional as F


class PoseLoss(nn.Module):
    def __init__(self):
        super(PoseLoss, self).__init__()
        self.mse_loss = nn.MSELoss()
        self.bce_loss = nn.BCELoss()

    def forward(self, predicted_poses, true_poses, eos_predictions, true_eos):
        # Pad poses
        max_size = max(predicted_poses.size(1), true_poses.size(1))
        predicted_poses = F.pad(predicted_poses, (0, 0, 0, max_size - predicted_poses.size(1)))
        true_poses = F.pad(true_poses, (0, 0, 0, max_size - true_poses.size(1)))
        # Pose loss (MSE)
        pose_loss = self.mse_loss(predicted_poses, true_poses)

        # Pad EOS
        eos_predictions = eos_predictions.squeeze(-1)
        max_size = max(eos_predictions.size(1), true_eos.size(1))
        eos_predictions = F.pad(eos_predictions, (0, max_size - eos_predictions.size(1)))
        true_eos = F.pad(true_eos, (0, max_size - true_eos.size(1)))
        # EOS loss (Binary Cross-Entropy)
        eos_loss = self.bce_loss(eos_predictions, true_eos)

        # Total loss
        total_loss = pose_loss + eos_loss
        return total_loss
