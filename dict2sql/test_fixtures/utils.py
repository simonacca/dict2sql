import os
import platform
import sqlite3

python_version = platform.python_version_tuple()

if int(python_version[0]) >= 3 and int(python_version[1]) >= 7:

    def open_sqlite_in_memory(filepath: str = "dict2sql/test_fixtures/chinhook.sqlite3"):
        disk_db = sqlite3.connect(f"file:{filepath}?mode=ro", uri=True)
        memory_db = sqlite3.connect(":memory:")

        disk_db.backup(memory_db)
        disk_db.close()
        return memory_db


else:

    def open_sqlite_in_memory(filepath: str = "dict2sql/test_fixtures/chinhook.sqlite3"):
        with open(filepath, "rb") as f:
            memory_db = sqlite3.connect(database=f.read())
        return memory_db
