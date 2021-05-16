import dict2sql.compiler_misc as comp
import dict2sql.types as t
from dict2sql.utils import Utils

from . import clause_where


class _DeleteClause:
    @staticmethod
    def to_sql(u: Utils, clause: t.DeleteStatement) -> t.Intermediate:
        if "Delete" not in clause:
            raise ValueError('"Delete" field missing')

        return [
            "DELETE FROM",
            u.sanitizer(clause["Delete"]["Table"]),
        ]


class DeleteStatement(comp.BaseAlternativeChild):
    match = t.isDeleteStatement

    @classmethod
    def to_sql(cls, u: Utils, clause: t.DeleteStatement) -> t.Intermediate:
        return [
            _DeleteClause.to_sql(u, clause),
            clause_where.WhereClause.to_sql(u, clause),
        ]
