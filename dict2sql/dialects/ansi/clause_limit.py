import dict2sql.compiler_misc as comp
import dict2sql.types as t
from dict2sql.utils import Utils


class _LimitClauseSingle(comp.BaseAlternativeChild):
    match = t.isLimitClause

    @classmethod
    def to_sql(cls, u: Utils, clause: t.LimitClause) -> t.Intermediate:
        return u.sanitizer(str(clause))


class LimitClause(comp.BaseAlternativeParentIfKey):
    alternatives = [_LimitClauseSingle]
    key = "Limit"

    @staticmethod
    def wrapper(u: Utils, clause: t.Intermediate):
        return ["LIMIT", clause]
