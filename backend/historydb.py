import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "historical_data.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def save_bars(
    symbol: str,
    secType: str,
    exchange: str,
    barSize: str,
    bars: list[dict],
) -> dict:
    if not bars:
        return {}

    # I maybe need to add logging to this....

    conn = get_connection()
    conn.executemany(
        """
        INSERT OR REPLACE INTO historical_bars
            (symbol, secType, exchange, barSize, date,
             open, high, low, close, volume, barCount, average)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                symbol,
                secType,
                exchange,
                barSize,
                bar["date"],
                bar["open"],
                bar["high"],
                bar["low"],
                bar["close"],
                bar["volume"],
                bar["barCount"],
                bar["average"],
            )
            for bar in bars
        ],
    )
    conn.commit()
    conn.close()

    return {"res": "Added data to Database"}


def daterange_to_ib_params(start_date: str, end_date: str) -> tuple[str, str]:
    """Converts a YYYYMMDD start/end date pair into the (endDateTime, durationStr)
    pair reqHistoricalData expects, since IB has no notion of a start date."""
    start = datetime.strptime(start_date, "%Y%m%d")
    end = datetime.strptime(end_date, "%Y%m%d")
    days = (end - start).days + 1

    endDateTime = end.strftime("%Y%m%d") + " 23:59:59 US/Eastern"
    duration = f"{days} D"

    return endDateTime, duration
