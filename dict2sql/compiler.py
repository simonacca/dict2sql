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
from typing import Any, List, Optional, Type

import dict2sql.types as t
from dict2sql.utils import Utils, interpose


class _Rule(abc.ABC):
    @classmethod
    @abc.abstractclassmethod
    def to_sql(cls, u: Utils, clause: Any) -> t.Intermediate:
        return ""


class _BaseAlternativeChild(_Rule, abc.ABC):
    @staticmethod
    @abc.abstractstaticmethod
    def match(clause: Any) -> bool:
        return False


class _BaseAlternativeChildAlwaysMatch(_BaseAlternativeChild):
    @staticmethod
    def match(clause: Any) -> bool:
        return True


class _BaseAlternativeParent:
    alternatives: Optional[List[Type[_BaseAlternativeChild]]]

    @staticmethod
    def wrapper(u: Utils, clause: t.Intermediate) -> t.Intermediate:
        # Identity wrapper (default)
        return clause

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
            raise ValueError(f"Could not find alternative")

    @classmethod
    def to_sql(cls, u: Utils, clause: Any) -> t.Intermediate:
        return cls.wrapper(u, cls.test_alternatives(u, clause))


class _BaseAlternativeParentIfKey(_BaseAlternativeParent, abc.ABC):
    key: Optional[str]

    @classmethod
    def to_sql(cls, u: Utils, clause: Any) -> t.Intermediate:
        if not isinstance(clause, dict) or not cls.key or cls.key not in clause:
            return []
        return super(_BaseAlternativeParentIfKey, cls).to_sql(u, clause[cls.key])


################################################################################
# Select


class _SelectClauseList(_BaseAlternativeChild):
    match = t.isColNameList

    @classmethod
    def to_sql(cls, u: Utils, clause: t.ColNameList) -> t.Intermediate:
        # No Col name
        return interpose(",", [u.sanitizer(x) for x in clause])


class _SelectClauseSingle(_BaseAlternativeChild):
    match = t.isColName

    @classmethod
    def to_sql(cls, u: Utils, clause: t.ColName) -> t.Intermediate:
        return _SelectClauseList.to_sql(u, [clause])


class _SelectClause(_BaseAlternativeParentIfKey):
    alternatives = [_SelectClauseSingle, _SelectClauseList]
    key = "Select"

    @staticmethod
    def wrapper(u: Utils, clause: t.Intermediate):
        return ["SELECT", clause]


################################################################################
# From


class _FromClauseSingle(_BaseAlternativeChild):
    match = t.isTableName

    @classmethod
    def to_sql(cls, u: Utils, clause: t.TableName) -> t.Intermediate:
        return u.format_tablename(u.sanitizer(clause))


class _FromClauseList(_BaseAlternativeChild):
    match = t.isTableNameList

    @classmethod
    def to_sql(cls, u: Utils, clause: List[t.FromClauseSub]) -> t.Intermediate:
        return interpose(
            ",",
            [_FromClause.test_alternatives(u, x) for x in clause],
        )


class _FromClauseSubQuery(_BaseAlternativeChild):
    match = t.isSubQuery

    @classmethod
    def to_sql(cls, u: Utils, clause: t.SubQuery) -> t.Intermediate:
        return [
            u.format_subquery(SelectStatement.to_sql(u, clause["Query"])),
            "AS",
            u.sanitizer(clause["Alias"]),
        ]


class _FromClauseJoin(_BaseAlternativeChild):
    match = t.isJoin

    @classmethod
    def to_sql(cls, u: Utils, clause: t.JoinClause) -> t.Intermediate:
        return u.format_subquery(
            [
                _FromClause.test_alternatives(u, clause["Sx"]),
                u.sanitizer(clause["Join"]),
                _FromClause.test_alternatives(u, clause["Dx"]),
                "ON",
                _WhereClause.test_alternatives(u, clause["On"]),
            ]
        )


class _FromClause(_BaseAlternativeParentIfKey):
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


################################################################################
# Where


class _ExpressionLiteralSimple(_BaseAlternativeChild):
    match = t.isExpressionLiteralSimple

    @classmethod
    def to_sql(cls, u: Utils, clause: t.ExpressionLiteralSimple) -> t.Intermediate:
        return u.sanitizer(clause)


class _ExpressionLiteralQuoted(_BaseAlternativeChild):
    match = t.isExpressionLiteralQuoted

    @classmethod
    def to_sql(cls, u: Utils, clause: t.ExpressionLiteralQuoted) -> t.Intermediate:
        return u.format_quotes(u.sanitizer(clause["Expression"]))


class _ExpressionLiteral(_BaseAlternativeParent, _BaseAlternativeChildAlwaysMatch):
    alternatives = [_ExpressionLiteralQuoted, _ExpressionLiteralSimple]

    @classmethod
    def to_sql(cls, u: Utils, clause: Any) -> t.Intermediate:
        return cls.wrapper(u, cls.test_alternatives(u, clause))


class _ExpressionBoolean(_BaseAlternativeChild):
    match = t.isExpressionBoolean

    @classmethod
    def to_sql(cls, u: Utils, clause: t.ExpressionBoolean) -> t.Intermediate:
        return u.format_subexpr(
            interpose(
                u.sanitizer(clause["Op"]),
                [_WhereClause.test_alternatives(u, x) for x in clause["Predicates"]],
            )
        )


class _ExpressionSxDx(_BaseAlternativeChild):
    match = t.isExpressionSxDx

    @classmethod
    def to_sql(cls, u: Utils, clause: t.ExpressionSxDx) -> t.Intermediate:
        return u.format_subexpr(
            [
                _WhereClause.test_alternatives(u, clause["Sx"]),
                u.sanitizer(clause["Op"]),
                _WhereClause.test_alternatives(u, clause["Dx"]),
            ]
        )


class _WhereClause(_BaseAlternativeParentIfKey):
    # TODO: Warning in this case the order matters in the list of alternatives/
    # (_ExpressionLiteral has to be last because it always matches)
    # is that ok? if yes, how to make this fact more explicit?
    alternatives = [_ExpressionBoolean, _ExpressionSxDx, _ExpressionLiteral]
    key = "Where"

    @staticmethod
    def wrapper(u: Utils, clause: t.Intermediate):
        return ["WHERE", clause]


################################################################################
# Limit


class _LimitClauseSingle(_BaseAlternativeChild):
    match = t.isLimitClause

    @classmethod
    def to_sql(cls, u: Utils, clause: t.LimitClause) -> t.Intermediate:
        return u.sanitizer(str(clause))


class _LimitClause(_BaseAlternativeParentIfKey):
    alternatives = [_LimitClauseSingle]
    key = "Limit"

    @staticmethod
    def wrapper(u: Utils, clause: t.Intermediate):
        return ["LIMIT", clause]


################################################################################
# Select statement


class SelectStatement(_BaseAlternativeChild):
    match = t.isSelectStatement

    @classmethod
    def to_sql(cls, u: Utils, clause: t.SelectStatement) -> t.Intermediate:
        return [
            _SelectClause.to_sql(u, clause),
            _FromClause.to_sql(u, clause),
            _WhereClause.to_sql(u, clause),
            _LimitClause.to_sql(u, clause),
        ]


################################################################################
# Insert statement
class _InsertClauseMap:
    @classmethod
    def to_sql(cls, u: Utils, clause: t.ValueMap) -> t.Intermediate:

        # impart a permanent sorting onto the items
        items = list(clause.items())

        return [
            u.format_subquery([u.format_colname(i[0]) for i in items]),
            "VALUES",
            u.format_subquery([u.format_quotes(i[1]) for i in items]),
        ]


class _InsertClause:
    @staticmethod
    def to_sql(u: Utils, clause: t.InsertStatement) -> t.Intermediate:
        return [
            "INSERT INTO",
            u.sanitizer(clause["Insert"]["Table"]),
            _InsertClauseMap.to_sql(u, clause["Insert"]["Data"]),
        ]


class InsertStatement(_BaseAlternativeChild):
    match = t.isInsertStatement

    @classmethod
    def to_sql(cls, u: Utils, clause: t.InsertStatement) -> t.Intermediate:
        return [
            _InsertClause.to_sql(u, clause),
        ]


################################################################################
# Update statement
class _UpdateClauseMap:
    @classmethod
    def to_sql(cls, u: Utils, clause: t.ValueMap) -> t.Intermediate:

        # impart a permanent sorting onto the items
        items = list(clause.items())

        return [
            [
                u.format_colname(i[0]),
                "=",
                u.format_quotes(i[1]),
            ]
            for i in items
        ]


class _UpdateClause:
    @staticmethod
    def to_sql(u: Utils, clause: t.UpdateStatement) -> t.Intermediate:
        return [
            "UPDATE",
            u.sanitizer(clause["Update"]["Table"]),
            "SET",
            _UpdateClauseMap.to_sql(u, clause["Update"]["Data"]),
        ]


class UpdateStatement(_BaseAlternativeChild):
    match = t.isUpdateStatement

    @classmethod
    def to_sql(cls, u: Utils, clause: t.UpdateStatement) -> t.Intermediate:
        return [
            _UpdateClause.to_sql(u, clause),
            _WhereClause.to_sql(u, clause),
        ]


################################################################################
# Statement


class Statement(_BaseAlternativeParent):
    alternatives = [SelectStatement, InsertStatement, UpdateStatement]

    @classmethod
    def to_sql_root(cls, u: Utils, clause: t.Statement):
        return u.format_query(cls.to_sql(u, clause))
