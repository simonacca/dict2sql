from typing import Any

import dict2sql.compiler_misc as comp
import dict2sql.types as t
from dict2sql.utils import Utils, interpose


class _ExpressionLiteralSimple(comp.BaseAlternativeChild):
    match = t.isExpressionLiteralSimple

    @classmethod
    def to_sql(cls, u: Utils, clause: t.ExpressionLiteralSimple) -> t.Intermediate:
        return u.sanitizer(clause)


class _ExpressionLiteralQuoted(comp.BaseAlternativeChild):
    match = t.isExpressionLiteralQuoted

    @classmethod
    def to_sql(cls, u: Utils, clause: t.ExpressionLiteralQuoted) -> t.Intermediate:
        return u.format_str_literal(clause["Expression"])


class ExpressionLiteral(comp.BaseAlternativeParent, comp.BaseAlternativeChildAlwaysMatch):
    alternatives = [_ExpressionLiteralQuoted, _ExpressionLiteralSimple]

    @classmethod
    def to_sql(cls, u: Utils, clause: Any) -> t.Intermediate:
        return cls.wrapper(u, cls.test_alternatives(u, clause))


class ExpressionBoolean(comp.BaseAlternativeChild):
    match = t.isExpressionBoolean

    @classmethod
    def to_sql(cls, u: Utils, clause: t.ExpressionBoolean) -> t.Intermediate:
        return u.format_subexpr(
            interpose(
                u.sanitizer(clause["Op"]),
                [WhereClause.test_alternatives(u, x) for x in clause["Predicates"]],
            )
        )


class ExpressionSxDx(comp.BaseAlternativeChild):
    match = t.isExpressionSxDx

    @classmethod
    def to_sql(cls, u: Utils, clause: t.ExpressionSxDx) -> t.Intermediate:
        return u.format_subexpr(
            [
                WhereClause.test_alternatives(u, clause["Sx"]),
                u.sanitizer(clause["Op"]),
                WhereClause.test_alternatives(u, clause["Dx"]),
            ]
        )


class WhereClause(comp.BaseAlternativeParentIfKey):
    # TODO: Warning in this case the order matters in the list of alternatives/
    # (_ExpressionLiteral has to be last because it always matches)
    # is that ok? if yes, how to make this fact more explicit?
    alternatives = [ExpressionBoolean, ExpressionSxDx, ExpressionLiteral]
    key = "Where"

    @staticmethod
    def wrapper(u: Utils, clause: t.Intermediate):
        return ["WHERE", clause]
