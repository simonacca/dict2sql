# dict2sql, the missing SQL API

dict2sql gives you the ability to express SQL as python data structures.

[![pypi badge](https://badge.fury.io/py/dict2sql.svg)](https://badge.fury.io/py/dict2sql)

# A simple example

```python
from dict2sql.types import SelectStatement
from dict2sql import dict2sql

query: SelectStatement = {
    "Select": ["name", "height", "country"],
    "From": ["mountains"],
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

```

produces

```sql
SELECT `name` , `height` , `country`
FROM `mountains`
WHERE ( ( height >= 3000 ) AND ( has_glacier = true ) )
LIMIT 3
```


# Installing

```shell
$ pip install -U dict2sql

```


# Notes


## Rationale

For historical reasons in the world of relational databases interfaces usually consist of domain-specific languages (mostly dialects of SQL)
rather than composition of data structures as it is common with modern APIs (for example JSON-based REST, protobuf).
While a domain-specific language (DSL) is very well suited for interactive use, such as manually exploring a dataset, this approach has some limitations when trying to interface with a database programmatically (for example from a Python script).

This library brings a modern API to SQL databases, allowing the user to express queries as composition of basic python data structures: dicts, lists, strings, ints, floats and booleans.

Among the primary benefits of this approach is a superior ability to reuse code. All the usual python constructs and software engineering best practices are available to the query author to express queries using clean, maintainable code.

Query-as-data also means compatibility with Python's type hinting system, which translates to reduced query-correctness issues, improved error messages (at least with respect to some query engines), and a quicker development experience.

Notably, this solution eliminates one major source of friction with traditional programming-language level handling of SQL: SQL injection and excaping. While solutions to this problem such as parametrized queries have been developed over time, they heavily favor safety at the expense of expressivity; it is usually forbidden to compose parametrized queries at runtime.
How is this accomplished? By having granular information about each component of a query, `dict2sql` is easily able to apply escaping where needed, resulting in safe queries.

Finally, it should be noted that this library strictly tries to do *one* job well, namely *composing sql queries*. There is many related functionalities in this space which we explicitely avoid taking on, feeling that they are best left to other very mature libraries in the Python ecosystem. For example: connecting to the database and performing queries, parsing query return values.

- code reuse
- types
- small concern, only translating to sql
- safety

## Implementation details
This project at the moment targets ANSI SQL, with the ambition of soon targeting all major SQL dialects.

Tests are based on the [Chinhook Database](https://github.com/lerocha/chinook-database).

## Best with

A user of this library would naturally want to obtain the results of queries as data structures as well (a sql2dict of sorts).
This functionality already provided by the excellent [records](https://pypi.org/project/records/) library.

## Contributing

Contributions and forks are welcome!

If you want to increment the current language to increase coverage of ANSI SQL, go right ahead.

If you plan to contribute major features such as support for a new dialect, it is recommended to start a PR early on in the development process to prevent duplicate work and ensure that it will be possible to merge the PR without any hiccups.

In any case, thank you for your contribution!


### TODOs
- implement sanitization/escaping correctly
- sql functionality
    - having
    - functions
    - aggregate
    - statements
        - create
- more examples
    - query end to end with sqlalchemy
    - generative examples
- handle different dialects
    - sqlite
    - mysql
    - postgres
- implement tests
    - unit tests
        - compiler to ir
        - ir to sql
        - utils
    - security
        - test for sql injection
            - fuzzing
            - generative testing
