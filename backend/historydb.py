import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "historical_data.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS historical_bars (
            symbol TEXT NOT NULL,
            secType TEXT NOT NULL,
            exchange TEXT NOT NULL,
            barSize TEXT NOT NULL,
            whatToShow TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            barCount INTEGER,
            average REAL,
            PRIMARY KEY (symbol, secType, exchange, barSize, whatToShow, date)
        )
    """)
    conn.commit()
    conn.close()


def save_bars(
    symbol: str,
    secType: str,
    exchange: str,
    barSize: str,
    whatToShow: str,
    bars: list[dict],
) -> None:
    if not bars:
        return

    conn = get_connection()
    conn.executemany(
        """
        INSERT OR REPLACE INTO historical_bars
            (symbol, secType, exchange, barSize, whatToShow, date,
             open, high, low, close, volume, barCount, average)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                symbol,
                secType,
                exchange,
                barSize,
                whatToShow,
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


def get_cached_range(
    symbol: str,
    secType: str,
    exchange: str,
    barSize: str,
    whatToShow: str,
    start_date: str,
    end_date: str,
) -> list[dict] | None:
    """Returns cached bars for [start_date, end_date] only if that whole range is
    covered by what's stored, otherwise None so the caller falls back to IB.
    Coverage is inferred from MIN/MAX date rather than tracking fetched ranges
    explicitly, so a previously fetched range with an internal gap would be
    (incorrectly) reported as covered -- acceptable here since bars are always
    fetched and stored as contiguous ranges from IB.
    """
    conn = get_connection()
    row = conn.execute(
        """
        SELECT MIN(date) as min_date, MAX(date) as max_date, COUNT(*) as cnt
        FROM historical_bars
        WHERE symbol=? AND secType=? AND exchange=? AND barSize=? AND whatToShow=?
        """,
        (symbol, secType, exchange, barSize, whatToShow),
    ).fetchone()

    if row["cnt"] == 0 or row["min_date"] > start_date or row["max_date"] < end_date:
        conn.close()
        return None

    rows = conn.execute(
        """
        SELECT date, open, high, low, close, volume, barCount, average
        FROM historical_bars
        WHERE symbol=? AND secType=? AND exchange=? AND barSize=? AND whatToShow=?
          AND date >= ? AND date <= ?
        ORDER BY date
        """,
        (symbol, secType, exchange, barSize, whatToShow, start_date, end_date),
    ).fetchall()
    conn.close()

    return [dict(r) for r in rows]


def daterange_to_ib_params(start_date: str, end_date: str) -> tuple[str, str]:
    """Converts a YYYYMMDD start/end date pair into the (endDateTime, durationStr)
    pair reqHistoricalData expects, since IB has no notion of a start date."""
    start = datetime.strptime(start_date, "%Y%m%d")
    end = datetime.strptime(end_date, "%Y%m%d")
    days = (end - start).days + 1

    endDateTime = end.strftime("%Y%m%d") + " 23:59:59 US/Eastern"
    duration = f"{days} D"

    return endDateTime, duration
