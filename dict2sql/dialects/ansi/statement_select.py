import dict2sql.compiler_misc as comp
import dict2sql.types as t
from dict2sql.utils import Utils

from . import clause_from, clause_limit, clause_select, clause_where


class SelectStatement(comp.BaseAlternativeChild):
    match = t.isSelectStatement

    @classmethod
    def to_sql(cls, u: Utils, clause: t.SelectStatement) -> t.Intermediate:
        return [
            clause_select.SelectClause.to_sql(u, clause),
            clause_from.FromClause.to_sql(u, clause),
            clause_where.WhereClause.to_sql(u, clause),
            clause_limit.LimitClause.to_sql(u, clause),
        ]
