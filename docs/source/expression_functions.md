# Expression Functions

## Overview

EDP expressions can use Python-like functions to pull data from any dataset, calculate statistics, or run advanced algorithms. Users are recommended to read the [Expressions documentation](https://quartzbio.freshdesk.com/en/support/solutions/articles/73000606023) for an in-depth review of use cases.


## Function Details

### **annotate**

Annotate a record with a template. Output data type: object

**Syntax**

```text
annotate(record, template, debug, include_errors)
```

-   record: (object) The record to be annotated
-   template: (str) The ID of the template
-   debug: (bool) Enable debug mode (default: False)
-   include\_errors: (bool) Include errors in output (default: True)

### **beacon**

Retrieves the beacon results for any entity. Output data type: object. Output object properties:

-   failed\_count: The number of datasets that failed (timed-out)
-   failed: List of datasets that failed (timed-out)
-   not\_found\_count: The number of datasets without results
-   found\_count: The number of datasets with results
-   found: List of datasets with results
-   not\_found: List of datasets without results

**Syntax**

```text
beacon(entity, entity_type, beacon_set, datasets, visibility)
```

-   entity: The entity value
-   entity\_type: A valid entity type
-   beacon\_set (optional): A valid beacon set ID
-   datasets (optional): A list of datasets to beacon
-   visibility (optional): Which datasets to beacon (default: vault)

### **classify_variant**

Classify a variant using one of multiple classifiers. Output data type: object

**Syntax**

```text
classify_variant(variant, classifier)
```

-   variant: The variant
-   classifier: The desired classifier (default: "germline")

### **coerce_list**

Coerce a value to a list. Single items will become a single value list. Lists will remain lists. None will return an empty list. Output data type: auto (list)

**Syntax**

-   value: The value to coerce to a list

### **concat**

Combine text from multiple lists or strings. Output data type: string

**Syntax**

```text
concat(values, delimiter)
```

-   values: The list of values to concatenate
-   delimiter (default: ""): The character to use in between values

### **crossmap**

Convert a variant or genomic region entity between different genome builds using the [Ensembl CrossMap](http://crossmap.sourceforge.net/) tool. The functionality of this expression is the same as UCSC's liftOver tool. Output data type: string

**Syntax**

```text
crossmap(entity, target_build)
```

-   entity: The entity (either a valid quartzbio variant BUILD-CHROMOSOME-START-STOP-ALT or genomic region BUILD-CHROMOSOME-START-STOP)
-   target\_build: The target genome build (GRCH37 or GRCH38)

**Examples**

`crossmap("GRCH38-13-32338647-32338647-T", "GRCH37")`

### **dataset_count**

Calculate the total number of results (or "hits") for a given query. Returns the number of results. Output data type: integer

**Syntax**

```text
dataset_count(dataset, entities, filters, query)
```

-   dataset: Any dataset with query permissions
-   entities (optional): A list of entity tuples: \[(entity\_type, entity)\]
-   filters (optional): A valid filter block
-   query (optional): A query string

### **dataset_entity_top_terms**

Retrieve the top entities for any entity field in a dataset. Returns a list of strings, in order of occurrence or None if the dataset can not be queried by this entity. Output data type: string (list)

**Syntax**

```text
dataset_entity_top_terms(dataset, entity, limit, filters, query)
```

-   dataset: Any dataset with query permissions
-   entity: The entity\_type to return within the dataset
-   limit (optional): The number of terms to retrieve (default: 1000)
-   filters (optional): Dataset filters
-   query (optional): A query string

**Examples**

`dataset_entity_top_terms("quartzbio:public:/ClinVar/5.1.0-20200720/Variants-GRCH38", "gene")`

### **dataset_field_percentiles**

Calculates the percentiles for any integer field. Returns an object containing the desired percentiles. Output data type: object

**Syntax**

```text
dataset_field_percentiles(dataset, field, percents, entities, filters, query)
```

-   dataset: Any dataset with query permissions
-   field: The field within the dataset
-   percents: The percentiles to calculate (default: 1, 5, 25, 50, 75, 95, 99)
-   entities (optional): A list of entity tuples: \[(entity\_type, entity)\]
-   filters (optional): Dataset filters
-   query (optional): A query string

### **dataset_field_stats**

Calculates statistics for any numeric field. Returns an object containing field statistics. Output data type: object. Output object properties:

-   count: The total number of values
-   max: The maximum value observed
-   sum: The sum of all values
-   avg: The average value
-   min: The minimum value observed

**Syntax**

```text
dataset_field_stats(dataset, field, entities, filters, query)
```

-   dataset: Any dataset with query permissions
-   field: The field within the dataset
-   entities (optional): A list of entity tuples: \[(entity\_type, entity)\]
-   filters (optional): Dataset filters
-   query (optional): A query string

### **dataset_field_terms_count**

Retrieve the number of unique terms for any string field in a dataset. Returns the number of unique terms. Output data type: integer

**Syntax**

```text
dataset_field_terms_count(dataset, field, entities, filters, query)
```

-   dataset: Any dataset with query permissions
-   field: The field within the dataset
-   entities (optional): A list of entity tuples: \[(entity\_type, entity)\]
-   filters (optional): Dataset filters
-   query (optional): A query string

**Examples**

`dataset_field_terms_count("quartzbio:public:/ClinVar/5.1.0-20200720/Variants-GRCh38", "clinical_significance")`

### **dataset_field_top_terms**

Retrieve the top terms for any string field in a dataset. Returns a list of objects containing the term and number of times it occurs, in order of occurrence. Output data type: object (list). Output object properties:

-   count: Number of times it occurs
-   term: Term value

**Syntax**

```text
dataset_field_top_terms(dataset, field, limit, entities, filters, query)
```

-   dataset: Any dataset with query permissions
-   field: The field within the dataset
-   limit (optional): The number of terms to retrieve (default: 10)
-   entities (optional): A list of entity tuples: \[(entity\_type, entity)\]
-   filters (optional): Dataset filters
-   query (optional): A query string

**Examples**

`dataset_field_top_terms("quartzbio:public:/ClinVar/5.1.0-20200720/Variants-GRCh38", "clinical_significance")`

### **dataset_field_values**

Retrieves a list of non-empty values for a dataset field. Returns a list of values from the specified field. Output data type: auto (list)

**Syntax**

```text
dataset_field_values(dataset, field, limit, entities, filters, query)
```

-   dataset: Any dataset with query permissions
-   field: The field within the dataset
-   limit (optional): The number of values to return (default: 10)
-   entities (optional): A list of entity tuples: \[(entity\_type, entity)\]
-   filters (optional): Dataset filters
-   query (optional): A query string

### **dataset_query**

Query any dataset with optional filters and/or entities. Returns a list of results. Output data type: object (list)

**Syntax**

```text
dataset_query(dataset, fields, limit, entities, filters, query)
```

-   dataset: Any dataset with query permissions
-   fields (optional): Fields to retrieve (default: all)
-   limit (optional): The number of values to return (default: 1)
-   entities (optional): A list of entity tuples: \[(entity\_type, entity)\]
-   filters (optional): Dataset filters
-   query (optional): A query string

**Examples**

`dataset_query("quartzbio:public:/ClinVar/5.1.0-20200720/Variants-GRCh38", fields=["clinical_significance"], query="*cancer*")`

`dataset_query("quartzbio:public:/ClinVar/5.1.0-20200720/Variants-GRCh38", entities=[["variant", "GRCH38-13-32357842-32357842-TA"]])`

### **datetime_format**

Format datetime strings. By default, it returns an ISO 8601 format date time string. To override, provide an optional input\_format or output\_format to be used. Output data type: string

**Syntax**

```text
datetime_format(value, input_format, output_format)
```

-   value: (str) A string containing a date/time stamp
-   input\_format: (str) The input format of the date (e.g. "%d/%m/%y %H:%M")
-   output\_format: (str) The output format of the date (ISO 8601 format is the default: "%Y-%m-%dT%H:%M:%S")

### **entity_ids**

Retrieve one or more entity IDs for a query. Output data type: string

**Syntax**

```text
entity_ids(entity_type, entity)
```

-   entity\_type: The entity type to retrieve
-   entity: The entity or query string

### **error**

Raise a FunctionError. Output data type: error

**Syntax**

-   message: An error message to raise

### **explode**

Split N values from M list fields into N records. If \_id is in the original record, each new record will have an integer appended to the \_id with the index of each exploded record. Output data type: object (list)

**Syntax**

-   record: (object) The record to be splitted
-   fields: (list or tuple) the fields IDs

### **findall**

Returns all non-overlapping matches of pattern in string, as a list of strings. The string is scanned left-to-right, and matches are returned in the order found. If one or more groups are present in the pattern, returns a list of groups. Output data type: string (list)

**Syntax**

```text
findall(pattern, string, regex_ignorecase, regex_dotall, regex_multiline)
```

-   pattern: The regular expression pattern
-   string: The string to search
-   regex\_ignorecase (default: None): With a "regex" pattern, will perform a case insensitive matching.
-   regex\_dotall (default: None): With a "regex" pattern, will make the "." special character match any character at all, including a newline; without this flag, "." will match anything except a newline.
-   regex\_multiline (default: None): With a "regex" pattern, when specified, the pattern character "^" matches at the beginning of the string and at the beginning of each line (immediately following each newline); and the pattern character "" matches at the end of the string and at the end of each line (immediately preceding each newline). By default, "^" matches only at the beginning of the string, and "" only at the end of the string and immediately before the newline (if any) at the end of the string.

### **genomic_sequence**

Retrieves a specific sequence from the genome. Output data type: string

**Syntax**

```text
genomic_sequence(genomic_region)
```

-   genomic\_region: A valid genomic region in the form: BUILD-CHROMOSOME-START-STOP

**Examples**

`genomic_sequence("GRCh37-5-36241400-36241700")`

### **get**

Get the value at any depth of a nested object based on the path described by `path`. If path doesn't exist, `default` is returned. Output data type: auto

**Syntax**

-   obj: (list|dict) The object to process
-   path: (str|list) List or `.` delimited string of path describing path.
-   default (keyword): Default value to return if path doesn't exist. Defaults to `None`.

### **melt**

Convert a wide dataset to a long dataset by "melting" one or more fields into "key" and "value" fields. All fields must have the same data type. Output data type: object (list)

**Syntax**

```text
melt(record, fields, key_field, value_field, melt_list_values)
```

-   record: (object) The record to be melted
-   fields: (list or tuple) the fields IDs
-   key\_field: (str) key field (default: "key")
-   value\_field: (str) value field (default: "value")
-   melt\_list\_values: (bool) (default: False)

### **normalize_aa_change**

Normalize an amino acid change (beta). Output data type: string

**Syntax**

```text
normalize_aa_change(aa_change, ref, alt)
```

-   aa\_change: The aa\_change
-   ref: (optional) Reference allele
-   alt: (optional) Alternate allele

### **normalize_variant**

Normalize a variant ID (minimal representation and left shifting). Output data type: string

**Syntax**

```text
normalize_variant(variant)
```

-   variant: The variant

### **now**

Retrieves the current date and time. Output data type: string

**Syntax**

-   timezone (default: EST): The timezone to use for the date
-   template (default: ISO 8601): The format in which to represent the date/time, defaults to ISO 8601 format (%Y-%m-%dT%H:%M:%S)

### **predict_variant_effects**

Predict the effects of a variant using Veppy. Output data type: object (list). Output object properties:

-   so\_term: The Sequence Ontology term
-   impact: The effect impact
-   so\_accession: The Sequence Ontology accession number
-   transcript: The affected transcript ID
-   lof: True if the mutation is predicted to cause the protein to lose its function

**Syntax**

```text
predict_variant_effects(variant, default_transcript, gene_model)
```

-   variant: The variant
-   default\_transcript (optional): If True, return effects for just the default transcript. If a specific transcript, then limits results to this transcript only. Otherwise returns effects for all transcripts.
-   gene\_model (optional): The desired gene model: refseq (default) or ensembl

**Examples**

`predict_variant_effects("GRCH38-7-117559590-117559593-A")`

### **prevalence**

Calculates the frequency that a value occurs within a population. Typically used to calculate the prevalence of variants or genes across samples in a dataset. Returns the frequency of occurrence. <u dir="ltr">Please note: in large datasets, the result is approximate and can have an error of up to 5%.&nbsp;</u> Output data type: double

**Syntax**

```text
prevalence(dataset, entity, sample_field, filters)
```

-   dataset: Any dataset with discover permissions
-   entity: A single entity tuple: (entity\_type, entity)
-   sample\_field: The field containing the sample IDs
-   filters (optional): Filters to apply on the dataset

### **search**

Scan through string looking for the first location where the regular expression pattern produces a match. Returns True on a match and False if no position in the string matches the pattern. Output data type: boolean

**Syntax**

```text
search(pattern, string, regex_ignorecase, regex_dotall, regex_multiline)
```

-   pattern: The regular expression pattern
-   string: The string to search
-   regex\_ignorecase (default: None): With a "regex" pattern, will perform a case insensitive matching.
-   regex\_dotall (default: None): With a "regex" pattern, will make the "." special character match any character at all, including a newline; without this flag, "." will match anything except a newline.
-   regex\_multiline (default: None): With a "regex" pattern, when specified, the pattern character "^" matches at the beginning of the string and at the beginning of each line (immediately following each newline); and the pattern character "" matches at the end of the string and at the end of each line (immediately preceding each newline). By default, "^" matches only at the beginning of the string, and "" only at the end of the string and immediately before the newline (if any) at the end of the string.

### **search_groups**

Scan through string looking for the first location where the regular expression pattern produces a match. Returns a list of strings corresponding to the groups in the pattern. Output data type: string (list)

**Syntax**

```text
search_groups(pattern, string, regex_ignorecase, regex_dotall, regex_multiline)
```

-   pattern: The regular expression pattern
-   string: The string to search
-   regex\_ignorecase (default: None): With a "regex" pattern, will perform a case insensitive matching.
-   regex\_dotall (default: None): With a "regex" pattern, will make the "." special character match any character at all, including a newline; without this flag, "." will match anything except a newline.
-   regex\_multiline (default: None): With a "regex" pattern, when specified, the pattern character "^" matches at the beginning of the string and at the beginning of each line (immediately following each newline); and the pattern character "" matches at the end of the string and at the end of each line (immediately preceding each newline). By default, "^" matches only at the beginning of the string, and "" only at the end of the string and immediately before the newline (if any) at the end of the string.

### **split**

Split text based on a delimiter and optionally strip whitespace. Output data type: string (list)

**Syntax**

```text
split(value, delimiter, regex, strip, regex_ignorecase, regex_dotall, regex_multiline)
```

-   value: The string to split
-   delimiter (default: any whitespace): The character(s) to split on
-   regex (default: None): A valid Python regular expression pattern to split on.
-   strip (default: True): Strip whitespace from each resulting value
-   regex\_ignorecase (default: None): With a "regex" pattern, will perform a case insensitive matching.
-   regex\_dotall (default: None): With a "regex" pattern, will make the "." special character match any character at all, including a newline; without this flag, "." will match anything except a newline.
-   regex\_multiline (default: None): With a "regex" pattern, when specified, the pattern character "^" matches at the beginning of the string and at the beginning of each line (immediately following each newline); and the pattern character "" matches at the end of the string and at the end of each line (immediately preceding each newline). By default, "^" matches only at the beginning of the string, and "" only at the end of the string and immediately before the newline (if any) at the end of the string.

### **sub**

Return the string obtained by replacing the leftmost non-overlapping occurrences of pattern in string by the replacement repl. If the pattern isn't found, string is returned unchanged. Output data type: string

**Syntax**

```text
sub(pattern, repl, string, count, regex_ignorecase, regex_dotall, regex_multiline)
```

-   pattern: The regular expression pattern
-   repl: The string to replace matches with
-   string: The string to search
-   count: (default: 0) The maximum number of pattern occurrences to be replaced.If zero, all occurrences will be replaces.
-   regex\_ignorecase (default: None): With a "regex" pattern, will perform a case insensitive matching.
-   regex\_dotall (default: None): With a "regex" pattern, will make the "." special character match any character at all, including a newline; without this flag, "." will match anything except a newline.
-   regex\_multiline (default: None): With a "regex" pattern, when specified, the pattern character "^" matches at the beginning of the string and at the beginning of each line (immediately following each newline); and the pattern character "" matches at the end of the string and at the end of each line (immediately preceding each newline). By default, "^" matches only at the beginning of the string, and "" only at the end of the string and immediately before the newline (if any) at the end of the string.

### **tabulate**

Converts a list of objects into a table (i.e. a two-dimensional array). Output data type: object (list)

**Syntax**

```text
tabulate(objects, fields, header)
```

-   objects: The list of objects
-   fields (optional): List of fields to include (default: all)
-   header (optional): Include a header row (default: True)

### **today**

Returns the current date. Output data type: string

**Syntax**

```text
today(timezone, template)
```

-   timezone (default: EST): The timezone to use for the date
-   template (default: YYYY-MM-DD): The format in which to represent the date

### **translate_variant**

Translate variant into a protein change. Output data type: object. Output object properties:

-   protein\_length: Number of amino acids in the protein
-   cdna\_change: cDNA change
-   protein\_change: Protein change
-   protein\_coordinates: A dictionary containing start and stop coordinatesand the affected transcript id
-   gene: HUGO gene symbol
-   transcript: The transcript ID
-   effects: list of effects

**Syntax**

```text
translate_variant(variant, gene_model, transcript, include_effects)
```

-   variant: The variant
-   gene\_model (optional): The desired gene model: refseq (default) or ensembl
-   transcript (optional): Limits results to this transcript only
-   include\_effects (optional): Returns the effects of the variant using Veppy

**Examples**

`translate_variant("GRCH38-7-117559590-117559593-A")`

`translate_variant("GRCH38-7-117559590-117559593-A", gene_model="ensembl")`

`translate_variant("GRCH38-7-117559590-117559593-A", transcript="NM_000492.3")`

`translate_variant("GRCH38-7-117559590-117559593-A", include_effects=True)`

### **user**

Returns the currently authenticated user.Output data type: object

Output object properties:

-   name: The user's full name.
-   email: The user's email address
