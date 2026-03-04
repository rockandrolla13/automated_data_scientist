"""timesfm — Foundation model forecasting wrapper (TimesFM / Chronos)."""

from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class TimesFMResult:
    forecast: np.ndarray
    horizon: int
    context_length: int
    model_name: str


def forecast_timesfm(
    series: pd.Series,
    horizon: int = 10,
    context_length: int = 512,
    model_name: str = "chronos",
) -> TimesFMResult:
    """Zero-shot forecast via foundation model. Falls back to naive if unavailable."""
    values = series.dropna().values[-context_length:]

    try:
        if model_name == "chronos":
            from chronos import ChronosPipeline
            import torch
            pipeline = ChronosPipeline.from_pretrained("amazon/chronos-t5-small",
                                                        device_map="auto", torch_dtype=torch.float32)
            context = torch.tensor(values, dtype=torch.float32).unsqueeze(0)
            fc = pipeline.predict(context, prediction_length=horizon)
            forecast = fc[0].median(dim=0).values.numpy()
        else:
            # Fallback: naive seasonal
            forecast = values[-horizon:]
    except ImportError:
        # No model installed — return naive forecast
        forecast = np.full(horizon, values[-1])

    return TimesFMResult(
        forecast=forecast, horizon=horizon,
        context_length=len(values), model_name=model_name,
    )


def compare_with_baseline(
    series: pd.Series,
    horizon: int,
    test_values: np.ndarray,
) -> pd.DataFrame:
    """Compare foundation model vs naive baseline."""
    fm_result = forecast_timesfm(series, horizon)
    naive = np.full(horizon, series.dropna().iloc[-1])

    fm_mae = np.mean(np.abs(fm_result.forecast[:len(test_values)] - test_values))
    naive_mae = np.mean(np.abs(naive[:len(test_values)] - test_values))

    return pd.DataFrame({
        "model": [fm_result.model_name, "naive"],
        "mae": [fm_mae, naive_mae],
    })


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    series = pd.Series(np.cumsum(rng.normal(0, 0.01, 600)))
    result = forecast_timesfm(series, horizon=10)
    print(f"Model: {result.model_name}, Forecast: {result.forecast}")
