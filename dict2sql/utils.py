from typing import Iterable, TypeVar, Union
import itertools

# pyright: reportMissingTypeStubs=false
import toolz
from .types import Intermediate, SqlText, ColName, TableName
import pprint


class Utils:
    """
    Utils is the mechanism to customize the runtime behavior of dict2sql.
    Usually the user should be well-served by the default Utils implementation.
    Extending and overriding these methods however is the way to go to exhert
    precise control over the final output.
    """

    def __init__(self, flag_debug_produce_ir: bool = False):
        self.flag_debug_produce_ir = flag_debug_produce_ir

    def sanitizer(self, raw: SqlText) -> SqlText:
        return f"{raw}"

    def format_colname(self, raw: ColName) -> ColName:
        return f"`{raw}`"

    def format_tablename(self, raw: TableName) -> ColName:
        return f"`{raw}`"

    def format_subquery(self, raw: Iterable[Intermediate]) -> Intermediate:
        return itertools.chain(["("], raw, [")"])

    def format_subexpr(self, raw: Intermediate) -> Intermediate:
        return itertools.chain(["("], raw, [")"])

    def format_query_join(self, raw: Intermediate) -> SqlText:
        "Default query formatter. This produces usable SQL."

        def inner(raw: Intermediate) -> str:
            if isinstance(raw, str):
                return raw
                # pyright: reportUnnecessaryIsInstance=false

            elif isinstance(raw, Iterable):
                # pyright: reportUnknownArgumentType=false
                return " ".join([inner(x) for x in raw if x])

            else:
                print(raw)
                raise ValueError("Unknown object in intermediate representation")

        return inner(raw)

    def _format_query_realize_intermediate_repr(
        self, raw: Intermediate
    ) -> Intermediate:
        def inner(raw: Intermediate) -> Intermediate:
            if isinstance(raw, str):
                return raw
            elif isinstance(raw, Iterable):
                # pyright: reportUnknownVariableType=false
                return list([inner(x) for x in raw if x])
            else:
                print(raw)
                raise ValueError("Unknown object in intermediate representation")

        return inner(raw)

    def format_query_list_prettyprint(self, raw: Intermediate) -> str:
        "Used for debugging"
        pp = pprint.PrettyPrinter(depth=60)
        return pp.pformat(self._format_query_realize_intermediate_repr(raw))

    def format_query(self, raw: Intermediate) -> str:
        "Set the default query formatter"
        if self.flag_debug_produce_ir:
            return self.format_query_list_prettyprint(raw)
        return self.format_query_join(raw)


_InterposeElem = TypeVar("_InterposeElem")
_InterposeSeq = TypeVar("_InterposeSeq")


def interpose(
    el: _InterposeElem, seq: Iterable[_InterposeSeq]
) -> Iterable[Union[_InterposeElem, _InterposeSeq]]:
    """
    Introduce el between each pair of items on seq.
    This function improves the type signature of toolz.interpose
    """
    if not seq:
        return []
    # pyright: reportUnknownArgumentType=false
    # pyright: reportUnknownVariableType=false
    # pyright: reportUnknownMemberType=false
    return toolz.interpose(el, seq)
