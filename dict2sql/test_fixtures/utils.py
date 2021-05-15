import sqlite3


def open_sqlite_in_memory(filepath: str = "dict2sql/test_fixtures/chinhook.sqlite3"):
    disk_db = sqlite3.connect(f"file:{filepath}?mode=ro")
    memory_db = sqlite3.connect(":memory:")
    disk_db.backup(memory_db)
    disk_db.close()
    return memory_db
