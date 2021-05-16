"""
These types represent the building blocks of SQL statements.
They are part of the public interface for this module.

Types that need it, have a corresponding isType function, which is used
to disambiguate types at runtime.
"""
from typing import Any, Callable, Dict, Iterable, List, Literal, TypedDict, Union

# Basic types

# Eventually we should move to this. At present however, isinstance() cannot handle these types
# see: https://github.com/python/mypy/issues/3325
# SqlText = NewType("SqlText", str)
# TableName = NewType("TableName", str)
# ColName = NewType("ColName", str)

SqlText = str
TableName = str
ColName = str

Intermediate = Union[SqlText, ColName, TableName, Iterable["Intermediate"]]


def isTableName(obj: Any):
    return isinstance(obj, TableName)


def isColName(obj: Any):
    return isinstance(obj, ColName)


# Sanitizer
SanitizerT = Callable[[SqlText], SqlText]


ColNameList = List[ColName]


def isColNameList(obj: Any):
    return isinstance(obj, list)


TableNameList = List[TableName]


def isTableNameList(obj: Any):
    return isinstance(obj, list)


# Select Clause

SelectClause = Union[ColName, ColNameList]

# From Clause

JoinType = Literal[
    "INNER JOIN",
    "OUTER JOIN",
    "CROSS JOIN",
    "LEFT JOIN",
    "RIGHT JOIN",
    "NATURAL JOIN",
]


class JoinClause(TypedDict):
    Join: JoinType
    Sx: "FromClause"
    Dx: "FromClause"
    On: "Expression"


def isJoin(obj: Any):
    return isinstance(obj, dict) and "Join" in obj


FromClauseSub = Union["SubQuery", TableName, JoinClause]
FromClause = Union[FromClauseSub, List[FromClauseSub]]

# Where Clause

ExpressionLiteralSimple = str


def isExpressionLiteralSimple(obj: Any):
    return isinstance(obj, ExpressionLiteralSimple)


class ExpressionLiteralQuoted(TypedDict):
    Type: Literal["Quoted"]
    Expression: ExpressionLiteralSimple


def isExpressionLiteralQuoted(obj: Any) -> bool:
    # pyright: reportUnknownVariableType=false
    return isinstance(obj, dict) and ("Type" in obj) and (obj["Type"] == "Quoted")


ExpressionLiteral = Union[ExpressionLiteralSimple, ExpressionLiteralQuoted]


def isExpressionLiteral(obj: Any) -> bool:
    return isExpressionLiteralSimple(obj) or isExpressionLiteralQuoted(obj)


ExpressionSxDxOp = Literal["=", "<", ">", "<=", ">="]


class ExpressionSxDx(TypedDict):
    Op: ExpressionSxDxOp
    Sx: ExpressionLiteral
    Dx: ExpressionLiteral


def isExpressionSxDx(clause: "Expression"):
    return "Op" in clause and clause["Op"] in ["=", "<", ">", "<=", ">="]


ExpressionBooleanOp = Literal["OR", "AND"]
ExpressionBooleanPredicates = List["Expression"]


class ExpressionBoolean(TypedDict):
    Op: ExpressionBooleanOp
    Predicates: ExpressionBooleanPredicates


def isExpressionBoolean(clause: "Expression"):
    return "Op" in clause and clause["Op"] in ["OR", "AND"]


Expression = Union[ExpressionBoolean, ExpressionSxDx]


WhereClause = Expression

# Limit Clause

LimitClause = int


def isLimitClause(clause: Any):
    return isinstance(clause, int)


# Select Statement


class SelectStatement(TypedDict, total=False):
    Select: SelectClause
    From: FromClause
    Where: WhereClause
    Limit: LimitClause


def isSelectStatement(obj: Any):
    return isinstance(obj, dict) and "Select" in obj


class SubQuery(TypedDict):
    Alias: TableName
    Query: SelectStatement


def isSubQuery(obj: Any):
    return isinstance(obj, dict) and "Alias" in obj


# Insert statement

ValueMap = Dict[ColName, Any]

# TODO: find better name
class ValueClause(TypedDict):
    Table: TableName
    Data: ValueMap


class InsertStatement(TypedDict):
    Insert: ValueClause


def isInsertStatement(obj: Any):
    return isinstance(obj, dict) and "Insert" in obj


# Update Statement


class UpdateStatement(TypedDict, total=False):
    Update: ValueClause
    Where: WhereClause


def isUpdateStatement(obj: Any):
    return isinstance(obj, dict) and "Update" in obj


# Statement

Statement = Union[SelectStatement, InsertStatement, UpdateStatement]
