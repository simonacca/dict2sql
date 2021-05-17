import itertools
import pprint
from typing import Iterable, Union

import dict2sql.utils as main_utils
from dict2sql.types import Identifier, Intermediate, SqlText


class Utils(main_utils.Utils):
    """
    Utils is the mechanism to customize the runtime behavior of dict2sql.
    Usually the user should be well-served by the default Utils implementation.
    Extending and overriding these methods however is the way to go to exhert
    precise control over the final output.
    """

    def __init__(self, flag_debug_produce_ir: bool = False):
        self.flag_debug_produce_ir = flag_debug_produce_ir

    def sanitizer(self, raw: SqlText) -> SqlText:
        safe = raw.replace('"', "").replace("'", "''")
        return safe

    def format_identifier(self, raw: Union[Identifier, Identifier, Identifier]) -> Identifier:
        return f'"{self.sanitizer(raw)}"'

    def format_str_literal(self, raw: SqlText) -> SqlText:
        return f"'{self.sanitizer(raw)}'"

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
                return " ".join([inner(x) for x in raw if x])

            else:
                print(raw)
                raise ValueError("Unknown object in intermediate representation")

        return inner(raw)

    def _format_query_realize_intermediate_repr(self, raw: Intermediate) -> Intermediate:
        def inner(raw: Intermediate) -> Intermediate:
            if isinstance(raw, str):
                return raw
            elif isinstance(raw, Iterable):
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
