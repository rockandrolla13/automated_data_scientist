"""transformer_forecaster — Temporal Fusion Transformer and custom transformers."""

from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class TransformerResult:
    train_losses: list[float]
    val_losses: list[float]
    best_epoch: int
    attention_weights: np.ndarray | None


def prepare_tft_dataset(
    df: pd.DataFrame,
    target: str,
    time_idx: str,
    group_ids: list[str],
    max_encoder_length: int = 60,
    max_prediction_length: int = 10,
):
    """Prepare pytorch_forecasting TimeSeriesDataSet."""
    from pytorch_forecasting import TimeSeriesDataSet

    training = TimeSeriesDataSet(
        df, time_idx=time_idx, target=target, group_ids=group_ids,
        max_encoder_length=max_encoder_length,
        max_prediction_length=max_prediction_length,
        time_varying_known_reals=[time_idx],
        time_varying_unknown_reals=[target],
    )
    return training


def build_tft(training_dataset, hidden_size: int = 32, attention_head_size: int = 4):
    """Build Temporal Fusion Transformer."""
    from pytorch_forecasting import TemporalFusionTransformer

    model = TemporalFusionTransformer.from_dataset(
        training_dataset,
        hidden_size=hidden_size,
        attention_head_size=attention_head_size,
        dropout=0.1,
        hidden_continuous_size=16,
        loss=None,  # default QuantileLoss
    )
    return model


def train_tft(model, train_dl, val_dl, epochs: int = 50, lr: float = 1e-3):
    """Train TFT with PyTorch Lightning."""
    import pytorch_lightning as pl

    trainer = pl.Trainer(
        max_epochs=epochs,
        enable_progress_bar=False,
        gradient_clip_val=0.1,
    )
    trainer.fit(model, train_dataloaders=train_dl, val_dataloaders=val_dl)

    return TransformerResult(
        train_losses=[], val_losses=[], best_epoch=epochs,
        attention_weights=None,
    )


if __name__ == "__main__":
    print("TransformerForecaster requires pytorch_forecasting + pytorch_lightning.")
    print("See prepare_tft_dataset() for data format requirements.")
