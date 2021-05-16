from functools import partial
from typing import Optional

from dict2sql.dialects.ansi.statement import Statement
from dict2sql.dialects.ansi.utils import Utils


class dict2sql:
    def __init__(self, utils: Optional[Utils] = None):
        ut = utils or Utils()
        self.to_sql = partial(Statement.to_sql_root, ut)
