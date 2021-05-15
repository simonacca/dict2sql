import unittest

import dict2sql
from dict2sql.test_fixtures.utils import open_sqlite_in_memory
from dict2sql.types import SelectStatement


class TestSqlite3(unittest.TestCase):
    def test_this(self):

        query: SelectStatement = {
            "Select": ["Title", "Artist.Name"],
            "From": {
                "Join": "INNER JOIN",
                "Sx": "Album",
                "Dx": "Artist",
                "On": {"Op": "=", "Sx": "Artist.ArtistId", "Dx": "Album.ArtistId"},
            },
            "Where": {
                "Op": "=",
                "Sx": "Artist.Name",
                "Dx": {"Type": "Quoted", "Expression": "AC/DC"},
            },
        }
        expectedRes = [
            ("For Those About To Rock We Salute You", "AC/DC"),
            ("Let There Be Rock", "AC/DC"),
        ]

        db = open_sqlite_in_memory()
        cur = db.cursor()
        t = dict2sql.dict2sql()
        res = list(cur.execute(t.to_sql(query)))
        self.assertEqual(res, expectedRes, "Wrong result")
