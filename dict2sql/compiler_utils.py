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
from dict2sql.utils import Utils


class Rule(abc.ABC):
    @classmethod
    @abc.abstractclassmethod
    def to_sql(cls, u: Utils, clause: Any) -> t.Intermediate:
        return ""


class BaseAlternativeChild(Rule, abc.ABC):
    @staticmethod
    @abc.abstractstaticmethod
    def match(clause: Any) -> bool:
        return False


class BaseAlternativeChildAlwaysMatch(BaseAlternativeChild):
    @staticmethod
    def match(clause: Any) -> bool:
        return True


class BaseAlternativeParent:
    alternatives: Optional[List[Type[BaseAlternativeChild]]]

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


class BaseAlternativeParentIfKey(BaseAlternativeParent, abc.ABC):
    key: Optional[str]

    @classmethod
    def to_sql(cls, u: Utils, clause: Any) -> t.Intermediate:
        if not isinstance(clause, dict) or not cls.key or cls.key not in clause:
            return []
        return super(BaseAlternativeParentIfKey, cls).to_sql(u, clause[cls.key])
