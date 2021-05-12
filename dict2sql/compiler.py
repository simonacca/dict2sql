"""
The compiler consists of the collection of rules to transform the data-structure
representation of a query into a valid SQL string.

Each class represents a portion of a SQL query:
from statements all the way down to expression and literals.

The classes here are organized in a hierarchy as follows (example):
- Statement
  - SelectStatement
    - SelectClause
    - FromClause
      - _FromClauseList
      - _FromClauseSubquery
"""
import abc

from typing import Any, Callable, List, Optional, Type
from dict2sql.utils import Utils, interpose
import dict2sql.types as t


class _BaseAlternative(abc.ABC):
    """ """

    @staticmethod
    @abc.abstractstaticmethod
    def match(clause: Any) -> bool:
        return False

    @staticmethod
    @abc.abstractstaticmethod
    def to_sql(u: Utils, clause: Any) -> t.Intermediate:
        return ""


class _BaseClause(abc.ABC):
    alternatives: Optional[List[Type[_BaseAlternative]]]
    wrapper: Callable[[Utils, Any], t.Intermediate]
    key: Optional[str]

    @classmethod
    def test_alternatives(cls, u: Utils, clause: Any) -> t.Intermediate:
        if not cls.alternatives:
            raise ValueError("Alternatives not implemented")
        for alternative in cls.alternatives:
            if alternative.match(clause):
                if u.flag_debug_produce_ir:
                    # Useful when looking at IR
                    return [alternative.__name__, alternative.to_sql(u, clause)]
                return alternative.to_sql(u, clause)
        else:
            raise ValueError("Could not find alternative")

    @classmethod
    def to_sql_bare(cls, u: Utils, clause: Any) -> t.Intermediate:
        return cls.wrapper(u, cls.test_alternatives(u, clause))

    @classmethod
    def to_sql_if_key(cls, u: Utils, clause: Any) -> t.Intermediate:
        if not isinstance(clause, dict) or not cls.key or cls.key not in clause:
            return f""
        return cls.to_sql_bare(u, clause[cls.key])

    # Make to_sql_if_key the default
    to_sql = to_sql_if_key


################################################################################
# Select


class _SelectClauseList(_BaseAlternative):
    match = t.isColNameList

    @staticmethod
    def to_sql(u: Utils, clause: t.ColNameList) -> t.Intermediate:
        return interpose(",", [u.format_colname(u.sanitizer(x)) for x in clause])


class _SelectClauseSingle(_BaseAlternative):
    match = t.isColName

    @staticmethod
    def to_sql(u: Utils, clause: t.ColName) -> t.Intermediate:
        return _SelectClauseList.to_sql(u, [clause])


class _SelectClause(_BaseClause):
    alternatives = [_SelectClauseSingle, _SelectClauseList]
    key = "Select"

    @staticmethod
    def wrapper(u: Utils, clause: t.Intermediate):
        return ["SELECT", clause]


################################################################################
# From


class _FromClauseSingle(_BaseAlternative):
    match = t.isTableName

    @staticmethod
    def to_sql(u: Utils, clause: t.TableName) -> t.Intermediate:
        return u.format_tablename(u.sanitizer(clause))


class _FromClauseList(_BaseAlternative):
    match = t.isTableNameList

    @staticmethod
    def to_sql(u: Utils, clause: List[t.FromClauseSub]) -> t.Intermediate:
        return interpose(
            ",",
            [_FromClause.test_alternatives(u, x) for x in clause],
        )


class _FromClauseSubQuery(_BaseAlternative):
    match = t.isSubQuery

    @staticmethod
    def to_sql(u: Utils, clause: t.SubQuery) -> t.Intermediate:
        return [
            u.format_subquery(SelectStatement.to_sql(u, clause["Query"])),
            "AS",
            u.sanitizer(clause["Alias"]),
        ]


class _FromClauseJoin(_BaseAlternative):
    match = t.isJoin

    @staticmethod
    def to_sql(u: Utils, clause: t.JoinClause) -> t.Intermediate:
        return u.format_subquery(
            [
                _FromClause.test_alternatives(u, clause["Sx"]),
                u.sanitizer(clause["Join"]),
                _FromClause.test_alternatives(u, clause["Dx"]),
                "ON",
                _WhereClause.test_alternatives(u, clause["On"]),
            ]
        )


class _FromClause(_BaseClause):
    alternatives = [
        _FromClauseSingle,
        _FromClauseList,
        _FromClauseSubQuery,
        _FromClauseJoin,
    ]
    key = "From"

    @staticmethod
    def wrapper(fc: Utils, clause: t.Intermediate):
        return ["FROM", clause]


################################################################################
# Where


class _ExpressionLiteral(_BaseAlternative):
    match = t.isExpressionLiteral

    @staticmethod
    def to_sql(u: Utils, clause: t.ExpressionLiteral) -> t.Intermediate:
        return u.sanitizer(clause)


class _ExpressionBoolean(_BaseAlternative):
    match = t.isExpressionBoolean

    @staticmethod
    def to_sql(u: Utils, clause: t.ExpressionBoolean) -> t.Intermediate:
        return u.format_subexpr(
            interpose(
                u.sanitizer(clause["Op"]),
                [_WhereClause.test_alternatives(u, x) for x in clause["Predicates"]],
            )
        )


class _ExpressionSxDx(_BaseAlternative):
    match = t.isExpressionSxDx

    @staticmethod
    def to_sql(u: Utils, clause: t.ExpressionSxDx) -> t.Intermediate:
        return u.format_subexpr(
            [
                _WhereClause.test_alternatives(u, clause["Sx"]),
                u.sanitizer(clause["Op"]),
                _WhereClause.test_alternatives(u, clause["Dx"]),
            ]
        )


class _WhereClause(_BaseClause):
    alternatives = [_ExpressionLiteral, _ExpressionBoolean, _ExpressionSxDx]
    key = "Where"

    @staticmethod
    def wrapper(u: Utils, clause: t.Intermediate):
        return ["WHERE", clause]


################################################################################
# Limit


class _LimitClauseSingle(_BaseAlternative):
    match = t.isLimitClause

    @staticmethod
    def to_sql(u: Utils, clause: t.LimitClause) -> t.Intermediate:
        return u.sanitizer(str(clause))


class _LimitClause(_BaseClause):
    alternatives = [_LimitClauseSingle]
    key = "Limit"

    @staticmethod
    def wrapper(u: Utils, clause: t.Intermediate):
        return ["LIMIT", clause]


################################################################################
# Select statement


# TODO: Doublecheck double inheritance!
class SelectStatement(_BaseAlternative):
    match = t.isSelectStatement

    @staticmethod
    def to_sql(u: Utils, clause: t.SelectStatement) -> t.Intermediate:
        return [
            _SelectClause.to_sql(u, clause),
            _FromClause.to_sql(u, clause),
            _WhereClause.to_sql(u, clause),
            _LimitClause.to_sql(u, clause),
        ]


################################################################################
# Statement


class Statement(_BaseClause):
    alternatives = [SelectStatement]

    @staticmethod
    def wrapper(u: Utils, clause: t.Intermediate):
        return clause

    @classmethod
    def to_sql(cls, u: Utils, clause: t.Statement) -> t.Intermediate:
        return cls.to_sql_bare(u, clause)

    @classmethod
    def to_sql_root(cls, u: Utils, clause: t.Statement) -> t.Intermediate:
        return u.format_query(cls.to_sql(u, clause))
