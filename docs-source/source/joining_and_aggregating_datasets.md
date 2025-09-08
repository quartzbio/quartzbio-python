# Joining and Aggregating Datasets

## Joining Datasets

### Overview

The EDP Python library enables users to join two datasets by keys (fields) that are related to each other. The provided datasets join functionality is very similar to the well-known left join in SQL.

The following example joins two public datasets, ClinVar and TCGA, on the variant field found in both datasets:

```Python
from quartzbio import Filter
from quartzbio import Dataset

#Write filter to narrow down results to pathogenic PTEN variants
filters = Filter(clinical_significance__exact="pathogenic") & Filter(gene__exact="PTEN")

#Query first dataset with filter and specify fields of interest
query_A = Dataset.get_by_full_path('quartzbio:Public:/ClinVar/5.2.0-20210110/Variants-GRCH37').query(filters=filters, fields=['variant', 'gene'])

#Query second dataset and specify fields of interest
query_B = Dataset.get_by_full_path('quartzbio:Public:/TCGA/2.0.0-2018-mc3-v0.2.8/SomaticMutations-GRCh37').query(fields=['existing_variation'])

# A result of datasets joining is a new Query object
join_query = query_A.join(query_B, key='variant', key_b='variant')

for record in join_query:
    print(record)

#Output:
{'gene': 'PTEN', 'variant': 'GRCH37-10-89624289-89624289-CG', 'existing_variation': None}
{'gene': 'PTEN', 'variant': 'GRCH37-10-89624274-89624274-G', 'existing_variation': 'rs587782187,CM110154,COSM346197,COSM921056,COSM28916'}
{'gene': 'PTEN', 'variant': 'GRCH37-10-89624275-89624275-T', 'existing_variation': 'CM110130,COSM5153'}
{'gene': 'PTEN', 'variant': 'GRCH37-10-89624275-89624275-T', 'existing_variation': 'CM110130,COSM5153'}
{'gene': 'PTEN', 'variant': 'GRCH37-10-89624275-89624275-T', 'existing_variation': 'CM110130,COSM5153'}
{'gene': 'PTEN', 'variant': 'GRCH37-10-89624275-89624275-T', 'existing_variation': 'CM110130,COSM5153'}
{'gene': 'PTEN', 'variant': 'GRCH37-10-89624275-89624275-T', 'existing_variation': 'CM110130,COSM5153'}
{'gene': 'PTEN', 'variant': 'GRCH37-10-89624275-89624277-C', 'existing_variation': None}
{'gene': 'PTEN', 'variant': 'GRCH37-10-89624278-89624279-G', 'existing_variation': None}
...
```

Users can add more datasets to the join query using the same key field. There is no limit to the number of additional joins but they may progressively slow down the query.

```Python
#Query additional dataset to be joined
query_C = Dataset.get_by_full_path('dataset_path').query(fields=["variant", "dataset_field"])

#Join additional dataset 
join_query = join_query.join(query_C, key='variant')

for record in join_query:
    print(record)
```

Filtering the output of join queries must be done client-side (i.e. within the user's Python code). For example, to find all the existing variation identifiers for the known pathogenic PTEN variants:

```Python
for record in join_query:
    if record['existing_variation'] is not None:
        print(record)

# Output:
{'gene': 'PTEN', 'variant': 'GRCH37-10-89624274-89624274-G', 'existing_variation': 'rs587782187,CM110154,COSM346197,COSM921056,COSM28916'}
{'gene': 'PTEN', 'variant': 'GRCH37-10-89624275-89624275-T', 'existing_variation': 'CM110130,COSM5153'}
{'gene': 'PTEN', 'variant': 'GRCH37-10-89624275-89624275-T', 'existing_variation': 'CM110130,COSM5153'}
{'gene': 'PTEN', 'variant': 'GRCH37-10-89624275-89624275-T', 'existing_variation': 'CM110130,COSM5153'}
{'gene': 'PTEN', 'variant': 'GRCH37-10-89624275-89624275-T', 'existing_variation': 'CM110130,COSM5153'}
{'gene': 'PTEN', 'variant': 'GRCH37-10-89624275-89624275-T', 'existing_variation': 'CM110130,COSM5153'}
...
```

### Advanced Example

The EDP join method enables users to join two datasets whose keys are lists. However, users must apply the explode [expression function](https://quartzbio.github.io/quartzbio-python/expression_functions.html) before joining:

```Python
import quartzbio as sb

ds1 = sb.Dataset.retrieve("dataset_id")
ds2 = sb.Dataset.retrieve("dataset_id")

# before joining the records, split each record by the values of ensembl_id
query_A = ds1.query(fields=["variant", "ensembl_id"], annotator_params={"pre_annotation_expression": 'explode(record, fields=["ensembl_id"])'})
query_B = ds2.query(fields=["gene", "ensembl_id"])

join_query = query_A.join(query_B, key="ensembl_id")

for record in join_query:
    print(record)

# To then put this into a new dataset
target = sb.Dataset.get_or_create_by_full_path('~/join_output')
join_query.migrate(target)
```

### Join Parameters

The join method has the following attributes:

|   **Parameter**    |  **Value**  |                                                                   **Description**                                                                    |
|----------------|---------|--------------------------------------------------------------------------------------------------------------------------------------------------|
|    query\_b    | object  |                                       Query object query\_B will be joined with the initial query query\_A.                                        |
|      key       | string  |                                  A key from query\_A containing a value that makes a relationship with query\_B.                                   |
|     key\_b     | string  | (Optional, default=None) a key from query\_B containing a value from a key from query\_A. If it is None a key argument from query\_A will be used. |
|     prefix     | string  |   (Optional, default=b\_) a prefix that will be added to all filtered fields from query\_B. If it is set to None, a random prefix will be used.    |
| always\_prefix | boolean |  (Optional, default=False) an option to add a prefix either always or only when it is necessary e.g. when both joining keys have the same name.  |

## Aggregating Datasets

### Overview

Both the EDP Python and R client libraries enable users to perform aggregations to build complex summaries of data. Aggregation queries can be run on datasets with the help of facets. Facets can be used to generate aggregated summaries of string (and date) fields as well as numeric fields, and they automatically work on top of [queries and filters](https://quartzbio.github.io/quartzbio-python/filters.html#overview). Facets can also be nested, which provides an incredibly efficient mechanism to summarize binned or rolled-up data (i.e. data summarized by term or by date).

### String and Date Aggregations

For string fields (i.e. categorical fields) and date fields, users can utilize facets to find the total number of unique values as well as a list of the most common values that occur in the dataset. When used with a filtered dataset, the results will represent the filtered subset of data.

The following facet types are supported:

-   **terms** (default): Returns a list of the top terms and the number of times they occur (in order of this value). The default number of terms returned at once is 10. Users can set a limit up to 1 million (1,000,000) terms returned.
-   **count**: Returns the number of unique values in the field. For very large datasets, this is an approximate number.

Facets will not work for text fields that are indexed (and tokenized) for full-text search. Terms facets are also disabled for \_id fields.

Examples in Python:
```Python
from quartzbio import Dataset
from quartzbio import Filter

query = Dataset.get_by_full_path('quartzbio:Public:/ClinVar/5.2.0-20210110/Variants-GRCH37').query()

# Find the most common genes in ClinVar
query.facets('gene')

# Retrieve the number of unique genes in ClinVar
query.facets(gene={'facet_type': 'count'})

# Filter ClinVar for only variants that relate to drug response.
# Which are the most common genes now?
f = quartzbio.Filter(clinical_significance='Drug response')
query.filter(f).facets('gene')

# How many genes are in this filtered query?
query.filter(f).facets(gene={'facet_type': 'count'})

# Now, get the top 100 most common values
query.filter(f).facets(gene={'limit': 100}
```

## Numeric Aggregations

There are various aggregation options are available for numerical fields (such as float/double, integer/long, and date). Instead of returning "common terms",  numerical facets can calculate summary statistics, histograms, and percentiles. The following facet types are supported:

-   **stats**: Default stats return average, count, maximum, minimum, and sum. Extended stats also include standard deviation, standard deviation lower and upper bounds, sum of squares, and variance.
-   **histogram**: values are binned according to a provided interval. For numerical fields, the default interval is 100. For dates, the default interval is 'month'. Histogram intervals must be integers, and will therefore not work for fields with values between 0 and 1 (such as allele frequencies).
-   **percentiles**: calculates estimated percentiles for a field. By default, returns the following percentiles: 1, 5, 25, 50, 75, 95, 99. Percentiles are approximated and have an 1-5% error for very large datasets.

Examples in Python:

```Python
from quartzbio import Dataset

query = Dataset.get_by_full_path('quartzbio:Public:/ClinVar/5.2.0-20210110/Variants-GRCH37').query()

# Get extended statistics for a numerical field.
query.facets(
    **{'info.ALLELEID': {
        'facet_type': 'stats', 'extended': True}})

# Calculate a histogram for genomic position in chromosome 12
# NOTE: We use **-style notation since "chromosome" and "start" are nested fields
query.filter(**{'genomic_coordinates.chromosome': 12}).facets(
    **{'genomic_coordinates.start': {
        'facet_type': 'histogram',
        'interval': 1000000}})
```

### Nested Aggregations

Nested aggregations can be used to apply an aggregation query to the result of another aggregation query. For example, given a dataset with patient information, users may want to determine the most common diagnosis age for each cancer type. Users could iterate through each cancer type and run a facets query on the age field, but that would require a large number of expensive API calls. Instead, by using nested aggregations, users can simply construct a facets query within an existing facets query, as in the example below.

At this time, users may only nest term and histogram facets under terms facets. Nesting within histogram facets is not currently supported.

The following example  yields the top ten genes associated with each disease in the public TCGA somatic mutations dataset:

In Python:
```Python
from quartzbio import Dataset

# Retrieve the TCGA Somatic Mutations dataset
tcga = Dataset.get_by_full_path('quartzbio:Public:/TCGA/2.0.0-2018-mc3-v0.2.8/SomaticMutations-GRCh37')

# Retrieve each disease (terms facets)
# and the associated gene (hugo_symbol) for each (nested terms facet)
facets = {
    'disease': {
        'limit': 100,
        'facets': {
            'hugo_symbol': {
                'limit': 10
            }
        }
    }
}

results = tcga.query().facets(**facets)

# Process the nested results
for disease, hugo_symbol, subfacets in results['disease']:
    print(disease, hugo_symbol, subfacets['hugo_symbol'])
    
#Output: 
#The disease is the first value in each row, followed by the total number of records and then each gene and its count
UCEC 934029 [['TTN', 2961], ['MUC16', 863], ['PTEN', 684], ['DST', 677], ['SYNE1', 642], ['CSMD3', 628], ['RYR2', 613], ['NEB', 569], ['ZFHX4', 551], ['OBSCN', 549]]

SKCM 494062 [['TTN', 3059], ['MUC16', 2022], ['DNAH5', 885], ['PCLO', 672], ['LRP1B', 515], ['ANK3', 494], ['GPR98', 482], ['CSMD1', 472], ['DNAH7', 460], ['CSMD2', 453]]

COAD 240187 [['TTN', 882], ['APC', 461], ['MUC16', 323], ['SYNE1', 300], ['TP53', 229], ['OBSCN', 220], ['FAT4', 211], ['RYR2', 186], ['NEB', 176], ['KRAS', 171]]

LUAD 222076 [['TTN', 935], ['MUC16', 562], ['RYR2', 488], ['CSMD3', 480], ['LRP1B', 392], ['USH2A', 374], ['ZFHX4', 348], ['TP53', 304], ['FLG', 269], ['XIRP2', 268]]
...
```