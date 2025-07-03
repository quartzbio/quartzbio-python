# Data Discoverty via API

Global Search allows users to search for vaults, files, folders, and datasets by name, tags, user, date, and other metadata that can be customized. Similarly to [Global Search on the web application](https://quartzbio.freshdesk.com/a/solutions/articles/73000597713), the search functionality is available through EDP Python and R clients as well. Users can refer to the [EDP Access and Search Programmatic Guide](https://quartzbio.freshdesk.com/en/support/solutions/articles/73000608178) to get started with using EDP clients.

## Global Search Basics

The EDP Global Search performs a search based on the provided set of parameters (filters, entities, query, limit, ordering, etc.):

-   query: Advanced search query string
-   filters: Filters to apply
-   entities: List of entity tuples to filter on (entity type, entity)
-   limit: Maximum number of query results to return

Python
```Python
from quartzbio import GlobalSearch

# Search returns all objects by default
results = GlobalSearch()
Python
```

Users may use the limit parameter to limit the number of returned objects:
```Python
# No filters applied with limit parameter
results = GlobalSearch(limit = 200)
```


## Applying filters for Global Search

Similar to the web application, users can apply filters with Python and R clients:

Python
```Python
from quartzbio import GlobalSearch

# Global Search object
search = GlobalSearch()

# Searching only for vaults
vaults = search.filter(type__in=["vault"])

# Searching based on date created
objects = search.filter(created_at__range=["2023-01-01","2023-12-31"])
```

## Advanced Search Query  

Users can refer to the [Advanced Search](https://quartzbio.freshdesk.com/a/solutions/articles/73000603094) documentation to learn how to write their own queries using the Query String syntax. This is also possible to do using Python and R clients by providing query parameters:

Python

```Python
from quartzbio import GlobalSearch

# Advanced search (using keyword argument)
results = GlobalSearch(query="TCGA")

# Advanced search (using positional argument)
results = GlobalSearch("test")
```

## Global Beacon Search  

Global Beacon Search, which is explained in the [Global Beacon Search article](https://quartzbio.freshdesk.com/a/solutions/articles/73000603092), can be performed as well with both Python and R clients by using the entities parameter. Please note that Global Beacon Search works only on datasets enabled by Global Beacons. To search for subjects or samples, users should also set the vault\_scope parameter to "any".

Python

```Python
 Entity search example
GlobalSearch(entities=[["gene", "BRCA2"]])

# Entity search example
GlobalSearch(entities=[["variant", "GRCH38-7-140753336-140753336-T"]])

# Sample entity search example
GlobalSearch(entities=[["sample", "A00001"]], vault_scope='any')
```

## Retrieving Subjects with Global Search 

Python
```Python
# Getting the subjects
search = GlobalSearch(entities=[["gene","BRCA2"]])
search.subjects()
```
