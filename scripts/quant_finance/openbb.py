"""openbb — Financial data access via OpenBB SDK (wrapper for common queries)."""

import pandas as pd


def get_equity_prices(
    symbol: str,
    start: str = "2020-01-01",
    end: str | None = None,
    provider: str = "yfinance",
) -> pd.DataFrame:
    """Fetch equity OHLCV data."""
    try:
        from openbb import obb
        data = obb.equity.price.historical(symbol=symbol, start_date=start, end_date=end, provider=provider)
        return data.to_df()
    except ImportError:
        # Fallback to yfinance directly
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        return ticker.history(start=start, end=end)


def get_macro_data(
    series_id: str,
    start: str = "2000-01-01",
    provider: str = "fred",
) -> pd.Series:
    """Fetch macro data (GDP, CPI, unemployment, etc.)."""
    try:
        from openbb import obb
        data = obb.economy.fred_series(series_id=series_id, start_date=start, provider=provider)
        df = data.to_df()
        return df.iloc[:, 0]
    except ImportError:
        raise ImportError("pip install openbb or yfinance as fallback")


def get_etf_holdings(symbol: str, provider: str = "fmp") -> pd.DataFrame:
    """Fetch ETF holdings."""
    try:
        from openbb import obb
        data = obb.etf.holdings(symbol=symbol, provider=provider)
        return data.to_df()
    except ImportError:
        raise ImportError("pip install openbb")


if __name__ == "__main__":
    print("OpenBB requires: pip install openbb (heavy, ~2GB)")
    print("Fallback: yfinance for equity prices")
    try:
        df = get_equity_prices("SPY", start="2024-01-01")
        print(f"SPY: {df.shape}, columns: {list(df.columns)}")
    except Exception as e:
        print(f"Error: {e}")
