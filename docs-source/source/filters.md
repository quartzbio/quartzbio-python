# Filters

## Overview

The EDP provides an easy-to-use, real-time API for [querying datasets and files](https://quartzbio.freshdesk.com/a/solutions/articles/73000612356) through the Python and R client libraries, which also enable the application of complex filters on dataset and file fields. Users can also utilize Bash to query and filter datasets.

Users can filter on any field in a dataset or file:

```Python
#Filter ClinVar dataset to pathogenic variants

dataset = Dataset.get_by_full_path('quartzbio:Public:/ClinVar/5.2.0-20210110/Variants-GRCH37')
dataset.query().filter(clinical_significance='pathogenic')

#Filter ClinVar file to pathogenic variants

clinvar = Object.get_by_full_path('quartzbio:Public:/ClinVar/5.2.0-20210110/ClinVar-5-2-0-20210110-Variants-GRCH37-1425664822266145048-20221110194518.json.gz')
clinvar.query().filter(clinical_significance='pathogenic')
```

Filters can be modified using "filter actions", which let users adjust the condition of a filter. To specify a filter action, users can append it to the field name when building a filter: 

```
<field>__<action> 
#For example, date__gte for filtering by dates greater or equal to the input
```

| Action       | Description                                                                                                     |
|--------------|-----------------------------------------------------------------------------------------------------------------|
| _iexact_ (default) | Field is equal to value (case-insensitive). If the field's value is a list, this will match values within the list, not the list as a whole. |
| _exact_      | Field is an exact match to value. Useful for case-sensitive string field queries.                               |
| _in_         | Field is "one of" a list of values. (similar to Python's `in` operator).                                        |
| _range_      | Field is a number within two values. Ranges are inclusive (fully closed).                                       |
| _gt_         | Field is a number greater than value.                                                                           |
| _lt_         | Field is a number less than value.                                                                              |
| _gte_        | Field is a number greater than or equal to value.                                                              |
| _lte_        | Field is a number less than or equal to value.                                                                 |
| _contains_   | Field contains this string value.                                                                              |
| _regexp_     | Field value matches this regular expression. (**Note: The action is only compatible with datasets**)            |

Some filter actions (`range`, `gt`, `lt`, `gte`, `lte`) may only be used on numeric and date fields.

Full-text fields use the `contains` filter action by default and act like a typical search would. Results are ordered by relevance based on the provided search terms. When using the `contains` action on string fields, the system converts the filter into a regular expression: `.*{VALUE}.*`, which is equivalent to the SQL expressions `%{VALUE}%`.

## String Filters

Users may filter string fields using the exact (or case-insensitive) match, regular expression match (`regexp`), or prefix match (`prefix`). Users can also match against multiple strings at once (a boolean _or_) using the "`in"` filter. By default, filters on string fields use the "equals" match.

In Python:

```Python
#Query Dataset
q = quartzbio.Dataset.get_by_full_path('quartzbio:Public:/ClinVar/5.2.0-20210110/Variants-GRCH37').query()

# Equals match
q.filter(gene='BRCA1')

# Equals match (in list)
q.filter(gene__in=['BRCA1', 'BRCA2'])

# Regular expression match
q.filter(gene__regexp='BRCA[12]')

# Prefix match
q.filter(gene__prefix='BRCA')
```

## Text Filters

Long (paragraph-length) fields typically use the `text` data type. The `"contains"` filter in text fields works more like a search than a filter. Results that match the search term are brought back in the order of relevance.


```Python
q = Dataset.get_by_full_path('quartzbio:Public:/MEDLINE/2.3.4-2018/MEDLINE-sample').query()

# Contains match for text fields
q.filter(abstract__contains='diabetes')
```

## Numeric & Date Filters

Numeric and date fields can be filtered by exact match, exact match in a list (`in`), half-open range match (`range`), and standard operators (`gt`, `lt`, `gte`, `lte`). Dates are in the format `YYYY-MM-DD`.


```Python
q = Dataset.get_by_full_path('quartzbio:Public:/ClinVar/5.2.0-20210110/Variants-GRCH37').query()

# Equals match
q.filter(info.ORIGIN=4)

# Equals match (in list)
q.filter(info.ORIGIN__in=[1, 2, 3])

# Range query
q.filter(info.ORIGIN__range=[1, 3])

# Operator query (gt/gte/lt/lte)
q.filter(info.ORIGIN__gt=4)
```

## Entity Filters

EDP-supported [Entities](https://quartzbio.github.io/quartzbio-python/metadata_and_global_beacons.html#entities) can be used for filtering, without requiring the exact field name that the Entity resides in. The entity filters are only compatible with datasets.


```Python
clinvar = Dataset.get_by_full_path('quartzbio:Public:/ClinVar/5.2.0-20210110/Variants-GRCH37'')

# Gene entity query
clinvar.query(entities=[['gene', 'BRCA2']])

# Variant entity query
clinvar.query(entities=[['variant', 'GRCH37-13-32890599-32890599-C']])
```

## Genomic Coordinate Filters

A dataset's genomic build is indicated by the suffix of the dataset's `full_path`. The genomic coordinate filters are only compatible with datasets.


```Python
# GRCh37
q = Dataset.get_by_full_path('quartzbio:Public:/ClinVar/5.2.0-20210110/Variants-GRCH37'').query()

# GRCh38
q = Dataset.get_by_full_path('quartzbio:Public:/ClinVar/5.2.0-20210110/Variants-GRCH38').query()

# Position (all overlapping features) - these two queries are equivalent
q.position('chr11', 18313400)
q.position(chromosome='11', position=18313400)

# Exact position only
q.position(chromosome='11', position=17552955, exact=True)

# Range (all overlapping features) - these two queries are equivalent
q.range('chr11', 18313300, 18315000)
q.range(chromosome='11', start=18313300, stop=18315000)

# Exact range only
q.range(chromosome='11', start=18313399, stop=18313403, exact=True)
```

## Combining Filters

The examples below show how to filter a dataset on one or two fields. In many cases, users will probably need to combine many filters into a single query.

When manually writing queries in JSON, users can combine and nest filters using boolean operators ('and', 'or', 'not'). In the Python client, users can combine filters using the `Filter` and `GenomicFilter` classes ("`&`" for "and", "`|`" for "or", and "`~`" for "not").


```Python
q = Dataset.get_by_full_path('quartzbio:Public:/ClinVar/5.2.0-20210110/Variants-GRCH37').query()

# AND
f = quartzbio.Filter(gene='BRCA1') & quartzbio.Filter(clinical_significance='pathogenic')
q.filter(f)

# OR
f = quartzbio.Filter(gene='BRCA1') | quartzbio.Filter(gene='BRCA2')
q.filter(f)

# NOT
f = ~ quartzbio.Filter(gene='BRCA1')
q.filter(f)
```

## Query Strings

Query strings are parsed into a series of terms and operators. A query string can be provided as part of an EDP dataset query in combination with filters, or as an alternative to filters.  The query strings are only compatible with datasets.

Terms in a query string can be single words - "quick" or "brown" - or a phrase surrounded by double quotes - "quick brown" - which will search for all the words in the phrase, in the same order. The query syntax is based on the [Lucene query syntax](https://lucene.apache.org/core/2_9_4/queryparsersyntax.html).

Queries are useful to find records that best match a word or phrase, relative to others. Filters are designed to reduce the potential result set by asking `yes/no` questions on every record in a dataset.

Query string operators allow users to customize a search. The available options are explained below:

### Field Names

By default, when no field names are specified, all string or text fields are searched for each term. Users can provide an explicit field name if they know the field in question:

```
status:active
```

Users can do an exact match on a specific field, for example:
```
gene:"BRCA1"
```

To search for one-or-more terms in a field, users can combine them with `OR` (default) or `AND`:
```
gene:(TTN) 
gene:(TTN OR BRCA1)
gene_family:(Olfactory AND receptors)
```

Users can also find records with missing fields:
```
_missing_:sample_id
```

Or, records where the field has a value (i.e. "not missing"):
```
_exists_:sample_id
```

### Wildcards

Wildcard searches can be run on individual terms, using `?` to replace a single character, and `*` to replace zero or more characters:
```
BRCA*
```

### Ranges

Ranges can be specified for almost any field data type. They are most useful for dates and numeric fields. Inclusive ranges are specified with square brackets `[min TO max]` and exclusive ranges with curly brackets `{min TO max}`.

For example, this query will retrieve records for all days in 2012:

```
date:[2012-01-01 TO 2012-12-31]

```

Similarly, users can also use ranges on numeric fields:
```
count:[1 TO 5]
```

And use infinite ranges:
```
count:[10 TO *]
```

Standard numeric comparison operators can also be used:

```
age:>10 age:>=10 age:<10 age:<=10
```

To combine an upper and lower bound with the simplified syntax, users can join two clauses with an `AND` operator:

```
age:(>=10 AND <20) age:(+>=10 +<20)
```

As processing ranges from a query string is much slower and less reliable than using an explicit range filter, users should try range filters first.

### Grouping

Multiple terms or clauses can be grouped together with parentheses to form sub-queries:

```
(Serine OR Cysteine) AND protease
```

Groups can be used to target a particular field, or to [boost](https://lucene.apache.org/core/2_9_4/queryparsersyntax.html#Boosting%20a%20Term) the result of a sub-query:

```
status:(active OR pending) title:(full text search)^2
```

### Reserved characters

The following characters are reserved in query strings and must be escaped with a leading backslash when used as part of a query term:

```
+ - = && || > < ! ( ) { } [ ] ^ " ~ * ? : \ /
```

For example, to search for the string `(1+1)=2`, the query should be written as `\(1\+1\)\=2`.

## Advanced Filters

Users can also compose filters in JSON and apply these filters via R, Python, or the EDP UI:


```Python
dataset = Dataset.get_by_full_path('quartzbio:Public:/MEDLINE/2.3.4-2018/MEDLINE-sample')

# Include all abstracts with "diabetes"
filters = [
    ["abstract__contains", "diabetes"]
]
dataset.query(filters=filters)

# Exclude all abstracts with "diabetes"
filters = [{
    "not": ["abstract__contains", "diabetes"]
}]
dataset.query(filters=filters)

# Find abstracts without "diabetes" from 1977
filters = [{
    "and": [
        {"not": ["abstract__contains", "diabetes"]},
        {
            "or": [
                ["date_published__regex", "*1977*"],
                ["date_created__range", ["1977-01-01", "1977-12-31"]]
            ]
        }
    ]
}]
dataset.query(filters=filters)
```

The advanced filter syntax is composed of the following elements:

-   `{OPERATOR}` is one of `AND`, `OR`, or `NOT`.
    
-   `{FIELD}` is a documented field name in the dataset.
    
-   `{ACTION}` is a valid field action in the format `{FIELD}__{ACTION}` (see below).
    
-   `{VALUE}` can be a string, numeric, or list value.
    

By default, a `{FIELD}` with no attached `{ACTION}` implies the "case-insensitive equals" (`iexact`) operator. Full-text (`text` data type) fields automatically use the `"contains"` filter action instead.

String and text actions include:

| Action    | Description                                                                                                         |
|-----------|---------------------------------------------------------------------------------------------------------------------|
| _iexact_  | (default for string/text) Field is equal to value (case-insensitive). If the field's value is a list, matches a value within the list, not the list as a whole. |
| _exact_   | Field is an exact match to value. Useful for longer string and text fields.                                         |
| _in_      | Field is "one of" a list of values.                                                                                |
| _contains_| Field contains this string value.                                                                                  |
| _regexp_  | Field value matches this regular expression. (**Note: The action is only compatible with datasets**)               |

Numeric and date field actions include:

| Action  | Description                                                                 |
|---------|-----------------------------------------------------------------------------|
| _exact_ | (default for numeric/date) Field is an exact match to value.               |
| _range_ | Field is a number within two values (inclusive/fully-closed).              |
| _gt_    | Field is a number greater than value.                                      |
| _lt_    | Field is a number less than value.                                         |
| _gte_   | Field is a number greater than or equal to value.                          |
| _lte_   | Field is a number less than or equal to value.                             |

