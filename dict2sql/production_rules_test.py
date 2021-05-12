from dict2sql.utils import Utils
import unittest
import dict2sql.production_rules as pr


class TestSelectRules(unittest.TestCase):
    def setUp(self) -> None:
        self._fc = Utils()

    def test_select_from_literal(self):
        res = pr.produce_select_from_literal(self._fc, "tst")
        self.assertEqual(res, r'`tst`')

    def test_select_from_literals(self):
        res = pr.produce_select_from_literals(self._fc, ["a", "b"])
        self.assertEqual(res, r"`a`, `b`")

    def test_select_clause(self):
        res = pr.produce_select_clause(self._fc, "abc")
        self.assertEqual(res, "SELECT abc")



class TestFromRules(unittest.TestCase):
    def setUp(self) -> None:
        self._fc = Utils()

    def test_from_clause_tablename(self):
        res = pr.produce_from_clause_tablename(self._fc, "tst")
        self.assertEqual(res, r'`tst`')

    def test_from_clause_subquery(self):
        res = pr.produce_from_clause_subquery(self._fc, "abc")
        self.assertEqual(res, r"(abc)")

    def test_from_clause_list(self):
        res = pr.produce_from_clause_list(self._fc, ["a", 'b'])
        self.assertEqual(res, "a, b")

    def test_from_clause(self):
        res = pr.produce_from_clause(self._fc, "abc")
        self.assertEqual(res, "FROM abc")


class TestWhereRules(unittest.TestCase):
    def setUp(self) -> None:
        self._fc = Utils()

    def test_where_clause_bool_and(self):
        res = pr.produce_where_clause_bool(self._fc, "AND", ["a", "b"])
        self.assertEqual(res, r'(a AND b)')

    def test_where_clause_bool_or(self):
        res = pr.produce_where_clause_bool(self._fc, "OR", ["a", "b"])
        self.assertEqual(res, r'(a OR b)')

    def test_where_clause_sxdx(self):
        res = pr.produce_where_clause_sxdx(self._fc, "=", "a", "b")
        self.assertEqual(res, r"((a) = (b))")


    def test_where_clause(self):
        res = pr.produce_where_clause(self._fc, "abc")
        self.assertEqual(res, "WHERE abc")

