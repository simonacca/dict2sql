from sqlite3.dbapi2 import Connection
import unittest
from typing import Any, Optional

import dict2sql
from dict2sql.test_fixtures.utils import open_sqlite_in_memory
from dict2sql.types import (
    InsertStatement,
    SelectStatement,
    Statement,
    UpdateStatement,
    WhereClause,
)


class _BaseTestQueryResult(unittest.TestCase):
    def _run_query(
        self,
        query: Statement,
        provided_db: Optional[Connection] = None,
    ):
        db = provided_db or open_sqlite_in_memory()
        cur = db.cursor()
        t = dict2sql.dict2sql()
        sql = t.to_sql(query)
        return list(cur.execute(sql))

    def _run_query_and_check_result(
        self,
        query: Statement,
        expectedResult: Any,
        provided_db: Optional[Connection] = None,
    ):
        res = self._run_query(query, provided_db)
        self.assertEqual(res, expectedResult, "Wrong result")


class TestSelect(_BaseTestQueryResult):
    def test_join(self):
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

        self._run_query_and_check_result(query, expectedRes)

    def test_where_boolean(self):
        query: SelectStatement = {
            "Select": ["FirstName"],
            "From": "Customer",
            "Where": {
                "Op": "AND",
                "Predicates": [
                    {
                        "Op": "=",
                        "Sx": "Country",
                        "Dx": {"Type": "Quoted", "Expression": "Canada"},
                    },
                    {
                        "Op": "=",
                        "Sx": "City",
                        "Dx": {"Type": "Quoted", "Expression": "Winnipeg"},
                    },
                ],
            },
        }

        expectedRes = [("Aaron",)]
        self._run_query_and_check_result(query, expectedRes)

    def test_select_star(self):
        query: SelectStatement = {"Select": "*", "From": "Customer", "Limit": 1}

        expectedRes = [
            (
                1,
                "Luís",
                "Gonçalves",
                "Embraer - Empresa Brasileira de Aeronáutica S.A.",
                "Av. Brigadeiro Faria Lima, 2170",
                "São José dos Campos",
                "SP",
                "Brazil",
                "12227-000",
                "+55 (12) 3923-5555",
                "+55 (12) 3923-5566",
                "luisg@embraer.com.br",
                3,
            )
        ]

        self._run_query_and_check_result(query, expectedRes)


class TestInsert(_BaseTestQueryResult):
    def test_insert(self):
        db = open_sqlite_in_memory()

        Name = "Weird Al Yancovic"
        insertQuery: InsertStatement = {
            "Insert": {"Table": "Artist", "Data": {"Name": Name}}
        }

        selectQuery: SelectStatement = {
            "Select": "Name",
            "From": "Artist",
            "Where": {
                "Op": "=",
                "Sx": "Name",
                "Dx": {"Type": "Quoted", "Expression": Name},
            },
        }

        self._run_query_and_check_result(selectQuery, [], db)

        self._run_query(insertQuery, db)

        expectedRes = [(Name,)]
        self._run_query_and_check_result(selectQuery, expectedRes, db)


class TestUpdate(_BaseTestQueryResult):
    def test_update(self):
        db = open_sqlite_in_memory()

        Name = "Weird Al Yancovic"
        Name2 = "Weird Al Yancovic ABC"

        whereSubQuery: WhereClause = {
            "Op": "=",
            "Sx": "Name",
            "Dx": {"Type": "Quoted", "Expression": Name},
        }

        insertQuery: InsertStatement = {
            "Insert": {"Table": "Artist", "Data": {"Name": Name}}
        }

        selectQuery: SelectStatement = {
            "Select": "Name",
            "From": "Artist",
            "Where": whereSubQuery,
        }

        self._run_query_and_check_result(selectQuery, [], db)

        self._run_query(insertQuery, db)

        expectedRes = [(Name,)]
        self._run_query_and_check_result(selectQuery, expectedRes, db)

        updateQuery: UpdateStatement = {
            "Update": {"Table": "Artist", "Data": {"Name": Name2}},
            "Where": whereSubQuery,
        }
        self._run_query(updateQuery, db)

        selectQuery2: SelectStatement = {
            "Select": "Name",
            "From": "Artist",
            "Where": {
                "Op": "=",
                "Sx": "Name",
                "Dx": {"Type": "Quoted", "Expression": Name2},
            },
        }

        expectedRes2 = [(Name2,)]
        self._run_query_and_check_result(selectQuery2, expectedRes2, db)