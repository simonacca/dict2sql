import dict2sql.compiler_misc as comp
import dict2sql.types as t
from dict2sql.utils import Utils

from . import clause_where


class _UpdateClauseMap:
    @classmethod
    def to_sql(cls, u: Utils, clause: t.ValueMap) -> t.Intermediate:

        # impart a permanent sorting onto the items
        items = list(clause.items())

        return [
            [
                u.format_identifier(i[0]),
                "=",
                u.format_str_literal(i[1]),
            ]
            for i in items
        ]


class _UpdateClause:
    @staticmethod
    def to_sql(u: Utils, clause: t.UpdateStatement) -> t.Intermediate:
        if "Update" not in clause:
            raise ValueError('"Update" field missing')

        return [
            "UPDATE",
            u.sanitizer(clause["Update"]["Table"]),
            "SET",
            _UpdateClauseMap.to_sql(u, clause["Update"]["Data"]),
        ]


class UpdateStatement(comp.BaseAlternativeChild):
    match = t.isUpdateStatement

    @classmethod
    def to_sql(cls, u: Utils, clause: t.UpdateStatement) -> t.Intermediate:
        return [
            _UpdateClause.to_sql(u, clause),
            clause_where.WhereClause.to_sql(u, clause),
        ]
