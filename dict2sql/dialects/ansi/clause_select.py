import dict2sql.compiler_misc as comp
import dict2sql.types as t
from dict2sql.utils import Utils, interpose


class _SelectClauseList(comp.BaseAlternativeChild):
    match = t.isColNameList

    @classmethod
    def to_sql(cls, u: Utils, clause: t.ColNameList) -> t.Intermediate:
        # No Col name
        return interpose(",", [u.sanitizer(x) for x in clause])


class _SelectClauseSingle(comp.BaseAlternativeChild):
    match = t.isColName

    @classmethod
    def to_sql(cls, u: Utils, clause: t.Identifier) -> t.Intermediate:
        return _SelectClauseList.to_sql(u, [clause])


class SelectClause(comp.BaseAlternativeParentIfKey):
    alternatives = [_SelectClauseSingle, _SelectClauseList]
    key = "Select"

    @staticmethod
    def wrapper(u: Utils, clause: t.Intermediate):
        return ["SELECT", clause]
