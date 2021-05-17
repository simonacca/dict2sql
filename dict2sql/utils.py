import abc
from typing import Iterable, TypeVar, Union

# pyright: reportMissingTypeStubs=false
import toolz

from dict2sql.types import Identifier, Intermediate, SqlText


class Utils(abc.ABC):
    """
    Utils is the mechanism to customize the runtime behavior of dict2sql.
    Usually the user should be well-served by the default Utils implementation.
    Extending and overriding these methods however is the way to go to exhert
    precise control over the final output.
    """

    flag_debug_produce_ir: bool

    @abc.abstractmethod
    def __init__(self, flag_debug_produce_ir: bool = False):
        pass

    @abc.abstractmethod
    def sanitizer(self, raw: SqlText) -> SqlText:
        pass

    @abc.abstractmethod
    # TODO: keep tablename,colname in the signature?
    def format_identifier(self, raw: Union[Identifier, Identifier, Identifier]) -> Identifier:
        pass

    @abc.abstractmethod
    def format_str_literal(self, raw: SqlText) -> SqlText:
        pass

    @abc.abstractmethod
    def format_subquery(self, raw: Iterable[Intermediate]) -> Intermediate:
        pass

    @abc.abstractmethod
    def format_subexpr(self, raw: Intermediate) -> Intermediate:
        pass

    @abc.abstractmethod
    def format_query_join(self, raw: Intermediate) -> SqlText:
        "Default query formatter. This produces usable SQL."
        pass

    @abc.abstractmethod
    def _format_query_realize_intermediate_repr(self, raw: Intermediate) -> Intermediate:
        pass

    @abc.abstractmethod
    def format_query_list_prettyprint(self, raw: Intermediate) -> str:
        pass

    @abc.abstractmethod
    def format_query(self, raw: Intermediate) -> str:
        pass


# Interpose

_InterposeElem = TypeVar("_InterposeElem")
_InterposeSeq = TypeVar("_InterposeSeq")


def interpose(el: _InterposeElem, seq: Iterable[_InterposeSeq]) -> Iterable[Union[_InterposeElem, _InterposeSeq]]:
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
