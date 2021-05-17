import dict2sql.compiler_misc as comp
import dict2sql.types as t
from dict2sql.utils import Utils


class _InsertClauseMap:
    @classmethod
    def to_sql(cls, u: Utils, clause: t.ValueMap) -> t.Intermediate:

        # impart a permanent sorting onto the items
        items = list(clause.items())

        return [
            u.format_subquery([u.format_identifier(i[0]) for i in items]),
            "VALUES",
            u.format_subquery([u.format_identifier(i[1]) for i in items]),
        ]


class _InsertClause:
    @staticmethod
    def to_sql(u: Utils, clause: t.InsertStatement) -> t.Intermediate:
        return [
            "INSERT INTO",
            u.sanitizer(clause["Insert"]["Table"]),
            _InsertClauseMap.to_sql(u, clause["Insert"]["Data"]),
        ]


class InsertStatement(comp.BaseAlternativeChild):
    match = t.isInsertStatement

    @classmethod
    def to_sql(cls, u: Utils, clause: t.InsertStatement) -> t.Intermediate:
        return [
            _InsertClause.to_sql(u, clause),
        ]
