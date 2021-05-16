import dict2sql.compiler_misc as comp
import dict2sql.types as t
from dict2sql.utils import Utils

from . import statement_insert, statement_select, statement_update


class Statement(comp.BaseAlternativeParent):
    alternatives = [
        statement_select.SelectStatement,
        statement_insert.InsertStatement,
        statement_update.UpdateStatement,
    ]

    @classmethod
    def to_sql_root(cls, u: Utils, clause: t.Statement):
        return u.format_query(cls.to_sql(u, clause))
