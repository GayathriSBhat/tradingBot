import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

from rich.console import Console
from rich.table import Table
from datetime import datetime


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


class RichTableHandler(logging.Handler):
    """Logging handler that prints each record as a single-row Rich table.

    Columns: Timestamp | Level | Message
    """
    def __init__(self, level=logging.NOTSET):
        super().__init__(level)
        self.console = Console()

    def emit(self, record: logging.LogRecord) -> None:
        try:
            ts = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
            level = record.levelname
            message = self.format(record)

            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("Timestamp", style="dim", no_wrap=True)
            table.add_column("Level", style="magenta")
            table.add_column("Message", overflow="fold")
            table.add_row(ts, level, message)

            self.console.print(table)
        except Exception:
            self.handleError(record)


def setup_logging(debug: bool = False, *, max_bytes: int = 10 * 1024 * 1024, backup_count: int = 5):
    """Configure logging with a Rich table console handler and a rotating file handler.

    - `debug`: sets logging level to DEBUG when True, INFO otherwise.
    - `max_bytes` / `backup_count`: configure rotation for the file handler.
    """
    level = logging.DEBUG if debug else logging.INFO

    root = logging.getLogger()
    # Clear existing handlers to avoid duplicates when re-initializing
    if root.handlers:
        for h in list(root.handlers):
            root.removeHandler(h)

    # File handler with rotation
    file_handler = RotatingFileHandler(LOG_DIR / "trading_bot.log", maxBytes=max_bytes, backupCount=backup_count)
    file_handler.setLevel(level)
    file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)

    # Rich table console handler for pretty output
    rich_table_handler = RichTableHandler()
    rich_table_handler.setLevel(level)
    rich_table_handler.setFormatter(logging.Formatter("%(message)s"))

    root.setLevel(level)
    root.addHandler(file_handler)
    root.addHandler(rich_table_handler)

    # Filter to allow only project/app logs in console/file (reduces noisy third-party logs)
    class ProjectFilter(logging.Filter):
        def __init__(self, project_id: str = "testTradeBot"):
            super().__init__()
            self.project_id = project_id

        def filter(self, record: logging.LogRecord) -> bool:
            try:
                if record.name.startswith("tradebot"):
                    return True
                pathname = getattr(record, "pathname", "") or ""
                return self.project_id in pathname
            except Exception:
                return False

    project_filter = ProjectFilter()
    file_handler.addFilter(project_filter)
    rich_table_handler.addFilter(project_filter)

    # Silence noisy HTTP libs further
    logging.getLogger("httpx").setLevel(logging.ERROR)
    logging.getLogger("httpcore").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.ERROR)


def attach_order_file_logger(level: int = logging.INFO, *, max_bytes: int = 10 * 1024 * 1024, backup_count: int = 5):
    """Attach a CSV rotating file handler for order-related logging.

    Returns the handler so the caller can remove it later with `detach_order_file_logger`.
    """
    root = logging.getLogger()
    csv_file = LOG_DIR / "trading_bot.log"
    handler = CSVRotatingFileHandler(str(csv_file), maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8')
    handler.setLevel(level)
    # Only log records belonging to the project or tradebot logger
    class _Filter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            try:
                if record.name.startswith("tradebot"):
                    return True
                pathname = getattr(record, "pathname", "") or ""
                return "testTradeBot" in pathname
            except Exception:
                return False

    handler.addFilter(_Filter())
    root.addHandler(handler)
    return handler


def detach_order_file_logger(handler: logging.Handler):
    root = logging.getLogger()
    try:
        root.removeHandler(handler)
        try:
            handler.close()
        except Exception:
            pass
    except Exception:
        pass

    # Reduce noise from third-party HTTP libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    # Ensure our app logger inherits configured handlers
    logging.getLogger("tradebot").setLevel(level)
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
import csv
import os

from rich.console import Console
from rich.table import Table


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


class RichTableHandler(logging.Handler):
    """Logging handler that prints each record as a single-row Rich table.

    Columns: Timestamp | Level | Message
    """
    def __init__(self, level=logging.NOTSET):
        super().__init__(level)
        self.console = Console()

    def emit(self, record: logging.LogRecord) -> None:
        try:
            ts = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
            level = record.levelname
            # Use the raw message for table to avoid duplicating timestamp/level
            message = record.getMessage()

            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("Timestamp", style="dim", no_wrap=True)
            table.add_column("Level", style="magenta")
            table.add_column("Message", overflow="fold")
            table.add_row(ts, level, message)

            self.console.print(table)
        except Exception:
            self.handleError(record)


class CSVRotatingFileHandler(RotatingFileHandler):
    """Rotating file handler that writes CSV rows: Timestamp, Level, Message.

    Uses csv.writer to safely quote messages.
    """
    def __init__(self, filename, maxBytes=0, backupCount=0, encoding=None):
        super().__init__(filename, maxBytes=maxBytes, backupCount=backupCount, encoding=encoding)
        # If file is new or empty, write header
        try:
            if not os.path.exists(self.baseFilename) or os.path.getsize(self.baseFilename) == 0:
                with open(self.baseFilename, "a", newline='', encoding=encoding or 'utf-8') as fh:
                    writer = csv.writer(fh)
                    writer.writerow(["Timestamp", "Level", "Message"])
        except Exception:
            pass

    def emit(self, record: logging.LogRecord) -> None:
        try:
            ts = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
            level = record.levelname
            message = record.getMessage()

            self.acquire()
            try:
                writer = csv.writer(self.stream)
                writer.writerow([ts, level, message])
                self.stream.flush()
            finally:
                self.release()
        except Exception:
            self.handleError(record)


def setup_logging(debug: bool = False, *, max_bytes: int = 10 * 1024 * 1024, backup_count: int = 5):
    """Configure logging with a Rich table console handler and a rotating CSV file handler.

    - `debug`: sets logging level to DEBUG when True, INFO otherwise.
    - `max_bytes` / `backup_count`: configure rotation for the file handler.
    """
    level = logging.DEBUG if debug else logging.INFO

    root = logging.getLogger()
    # Clear existing handlers to avoid duplicates when re-initializing
    if root.handlers:
        for h in list(root.handlers):
            root.removeHandler(h)

    # CSV file handler with rotation
    csv_file = LOG_DIR / "trading_bot.log"
    file_handler = CSVRotatingFileHandler(str(csv_file), maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8')
    file_handler.setLevel(level)

    # Rich table console handler for pretty output
    rich_table_handler = RichTableHandler()
    rich_table_handler.setLevel(level)

    root.setLevel(level)
    root.addHandler(file_handler)
    root.addHandler(rich_table_handler)
