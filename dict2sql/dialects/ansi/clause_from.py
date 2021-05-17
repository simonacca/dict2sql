from typing import List

import dict2sql.compiler_misc as comp
import dict2sql.types as t
from dict2sql.utils import Utils, interpose

from . import clause_where, statement_select


class _FromClauseSingle(comp.BaseAlternativeChild):
    match = t.isTableName

    @classmethod
    def to_sql(cls, u: Utils, clause: t.Identifier) -> t.Intermediate:
        return u.format_identifier(clause)


class _FromClauseList(comp.BaseAlternativeChild):
    match = t.isTableNameList

    @classmethod
    def to_sql(cls, u: Utils, clause: List[t.FromClauseSub]) -> t.Intermediate:
        return interpose(
            ",",
            [FromClause.test_alternatives(u, x) for x in clause],
        )


class _FromClauseSubQuery(comp.BaseAlternativeChild):
    match = t.isSubQuery

    @classmethod
    def to_sql(cls, u: Utils, clause: t.SubQuery) -> t.Intermediate:
        return [
            u.format_subquery(statement_select.SelectStatement.to_sql(u, clause["Query"])),
            "AS",
            u.sanitizer(clause["Alias"]),
        ]


class _FromClauseJoin(comp.BaseAlternativeChild):
    match = t.isJoin

    @classmethod
    def to_sql(cls, u: Utils, clause: t.JoinClause) -> t.Intermediate:
        return u.format_subquery(
            [
                FromClause.test_alternatives(u, clause["Sx"]),
                u.sanitizer(clause["Join"]),
                FromClause.test_alternatives(u, clause["Dx"]),
                "ON",
                clause_where.WhereClause.test_alternatives(u, clause["On"]),
            ]
        )


class FromClause(comp.BaseAlternativeParentIfKey):
    alternatives = [
        _FromClauseSingle,
        _FromClauseList,
        _FromClauseSubQuery,
        _FromClauseJoin,
    ]
    key = "From"

    @staticmethod
    def wrapper(u: Utils, clause: t.Intermediate):
        return ["FROM", clause]
