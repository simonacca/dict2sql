from dict2sql.types import SelectStatement
from dict2sql import dict2sql

query: SelectStatement = {
    "Select": ["name", "height", "country"],
    "From": [{
        "Join": "INNER JOIN",
        "Sx": "mountains",
        "Dx": "castles",
        "On": {
            "Op": "=",
            "Sx": "mountains.province",
            "Dx": "castle.province"
        }
    }],
    "Where": {
        "Op": "AND",
        "Predicates": [
            {"Op": ">=", "Sx": "height", "Dx": "3000"},
            {"Op": "=", "Sx": "has_glacier", "Dx": "true"}
        ],
    },
    "Limit": 3
}

dict2sql = dict2sql()

print(dict2sql.to_sql(query))

