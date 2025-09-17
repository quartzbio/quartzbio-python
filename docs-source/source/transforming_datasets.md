# Transforming Datasets

## Overview

The EDP makes it easy to transform data using its dynamic, Python-based expression language. Users can employ expressions to transform data when importing files when copying data between (or within) datasets (using "migrations"), or even when querying datasets. In all scenarios, expressions can be provided through the `target_fields` parameter. Users can refer to the [Expressions](https://quartzbio.github.io/quartzbio-python/expressions.html) documentation to learn more about using expressions.

This article describes how to transform data using dataset migrations, but users can use the same techniques with dataset imports. With dataset migrations, users can copy data between datasets as well as modify datasets in-place. This makes it possible to add, edit, and remove fields as well as records. All dataset migrations have a source dataset and a target dataset (which can be the same when editing a single dataset). Users are recommended to review the [Creating and Migrating Datasets](https://quartzbio.github.io/quartzbio-python/creating_and_migrating_datasets.html) documentation before this article.

## Modifying Fields

### Add Fields

The most common dataset transformation is to add a field to a dataset (also known as annotating the dataset or inserting a column). Fields can be added or modified using the `target_fields` parameter, which should contain a list of valid dataset fields. Any new fields in `target_fields` will be automatically detected and added to the dataset's schema. Adding fields requires the use of the upsert or overwrite commit mode, depending on the desired effect. This will ensure that the records are updated in-place (based on their \_id value), and not duplicated. To add multiple fields and transform data in a specific way, users can also create a reusable [Dataset Template](https://quartzbio.github.io/quartzbio-python/dataset_templates.html). 

In the following example, a new field will be added to a dataset "in-place", using the upsert commit mode:

In Python:
```Python
from quartzbio import Dataset

# Retrieve the source dataset
source = Dataset.get_by_full_path('quartzbio:Public:/ClinVar/5.2.0-20210110/Variants-GRCH37')

# Create a new target dataset in personal vault
target = Dataset.get_or_create_by_full_path('~/python_examples/clinvar')

# Apply filter to copy only subset of records from source
# Copy all variants in BRCA1
query = source.query().filter(gene='BRCA1')
query.migrate(target=target)

dataset = Dataset.get_or_create_by_full_path('~/python_examples/clinvar')

fields = [
    {
        'name': 'clinsig_clone',
        'expression': 'record.clinical_significance',
        'description': 'A copy of the current clinical_significance value',
        'data_type': 'string'
    }
]

# The source and target are the same dataset, which edits the dataset in-place
dataset.migrate(target=dataset, target_fields=fields, commit_mode='upsert')
```

### Edit Fields

In the following example, an existing field in the dataset from the previous example (clinsig\_clone) is modified (converted to uppercase). Similar to the example above, a commit mode of overwrite or upsert is required to avoid duplicating records. 

This example uses an expression that references a pre-existing field in the dataset; users can learn more about expression context by reviewing the [Expressions](https://quartzbio.github.io/quartzbio-python/expressions.html#overview) documentation.


```Python
from quartzbio import Dataset

dataset = Dataset.get_or_create_by_full_path('~/python_examples/clinvar')

fields = [
    {
        # Convert your copied "clinical_significance" values to uppercase.
        'name': 'clinsig_clone',
        'data_type': 'string',
        'expression': 'value.upper()'
    }
]

# The source and target are the same dataset, which edits the dataset in-place
dataset.migrate(target=dataset, target_fields=fields, commit_mode='upsert')
```

### Remove Fields

Fields cannot be removed from a dataset in-place so removing a field requires a new empty target dataset; all the data must be migrated to a new target dataset with the removed field(s) excluded from the source dataset.

In the following example, the field (clinsig\_clone) in the source dataset is removed by the dataset migration. Since a field is removed, the target dataset must be a new dataset (or one without the field). In this scenario, any commit mode can be used unless the user intends to overwrite records in the target dataset.

The example follows from the previous one:



```Python
from quartzbio import Dataset

# Use the dataset from the example above
source = Dataset.get_or_create_by_full_path('~/python_examples/clinvar')

# To remove a field, you need to create a new, empty dataset first.
target = Dataset.get_or_create_by_full_path('~/python_examples/clinvar_lite')

# Exclude the copied field from the example above
query = source.query(exclude_fields=['clinsig_clone'])
query.migrate(target=target, commit_mode='upsert')
```

To only remove the data (field values) from a specified field, users can run an upsert migration and use an expression to set the values to None (Python's equivalent to NULL).

### Transient Fields

Transient fields are like variables in a programming language. They can be used in a complex transform that requires intermediate values that are not meant to be stored in the dataset. Transient fields can be referenced by other expressions, but are not added to the dataset's schema or stored. Users can set the parameter `is_transient` to True and ensure that the field's ordering parameter evaluates the transient fields in the right order.

The following example uses transient fields to structure a few VCF records, leaving the variant IDs and dbSNP rsIDs in the resulting dataset:



```Python
from quartzbio import Dataset

dataset = Dataset.get_or_create_by_full_path('~/python_examples/transient_test')

# Sample of a VCF file
vcf = """CHROM POS     ID        REF ALT    QUAL FILTER INFO                              FORMAT      NA00001        NA00002        NA00003
20     14370   rs6054257 G      A       29   PASS   NS=3;DP=14;AF=0.5;DB;H2           GT:GQ:DP:HQ 0|0:48:1:51,51 1|0:48:8:51,51 1/1:43:5:.,.
20     17330   .         T      A       3    q10    NS=3;DP=11;AF=0.017               GT:GQ:DP:HQ 0|0:49:3:58,50 0|1:3:5:65,3   0/0:41:3
20     1110696 rs6040355 A      G     67   PASS   NS=2;DP=10;AF=0.333,0.667;AA=T;DB GT:GQ:DP:HQ 1|2:21:6:23,27 2|1:2:0:18,2   2/2:35:4
20     1230237 .         T      T       47   PASS   NS=3;DP=13;AA=T                   GT:GQ:DP:HQ 0|0:54:7:56,60 0|0:48:4:51,51 0/0:61:2
20     1234567 microsat1 GTCT   GTACT 50   PASS   NS=3;DP=9;AA=G                    GT:GQ:DP    0/1:35:4       0/2:17:2       1/1:40:3
""".splitlines()
# Extract the records (without the header)
records = [{'row': row} for row in vcf[1:]]

target_fields = [
    {
        "name": "header",
        "is_transient": True,
        "ordering": 1,
        "data_type": "string",
        "is_list": True,
        "expression": vcf[0].split()
    },
    {
        "name": "row",
        "is_transient": True,
        "ordering": 1,
        "data_type": "object",
        "expression": "dict(zip(record.header, value.split()))"
    },
    {
        "name": "build",
        "is_transient": True,
        "ordering": 1,
        "data_type": "string",
        "expression": "'GRCh37'"
    },
    {
        "name": "variant",
        "ordering": 2,
        "data_type": "string",
        "entity_type": "variant",
        "expression": """
            '-'.join([
                record.build,
                record.row['CHROM'],
                record.row['POS'],
                record.row['POS'],
                record.row['ALT']
            ])
        """
    },
    {
        "name": "rsid",
        "data_type": "string",
        "ordering": 2,
        "expression": "get(record, 'row.ID') if get(record, 'row.ID') != '.' else None"
    }
]

imp = DatasetImport.create(
    dataset_id=dataset.id,
    records=records,
    target_fields=target_fields)

dataset.activity(follow=True)

for record in dataset.query(exclude_fields=['_id', '_commit']):
    print(record)

# {'rsid': 'rs6054257' , 'variant': 'GRCh37-20-14370-14370-A'}
# {'rsid': None        , 'variant': 'GRCh37-20-17330-17330-A'}
# {'rsid': 'rs6040355' , 'variant': 'GRCh37-20-1110696-1110696-G'}
# {'rsid': None        , 'variant': 'GRCh37-20-1230237-1230237-T'}
# {'rsid': 'microsat1' , 'variant': 'GRCh37-20-1234567-1234567-GTACT'}
```

## Modifying Records

### Overwrite Records

In order to completely overwrite specific records in a dataset, users can utilize the overwrite commit mode. Users will need to know the \_id of the records they wish to overwrite, which can be retrieved by querying the dataset.

In the following example, a few records will be imported and then edited:


```Python
from quartzbio import Dataset
from quartzbio import DatasetImport

dataset = Dataset.get_or_create_by_full_path('~/python_examples/edit_records')

# Initial Import
imp = DatasetImport.create(
    dataset_id=dataset.id,
    records=[
        {'name': 'Francis Crick', 'birth_year': '1916'},
        {'name': 'James Watson', 'birth_year': '1928'},
        {'name': 'Rosalind Franklin', 'birth_year': '1920'}
    ]
)

# Retrieve the record to edit
record = dataset.query().filter(name='Francis Crick')[0]
record['name'] = 'Francis Harry Compton Crick'
record['awards'] = ['Order of Merit', 'Fellow of the Royal Society']

# Overwrite mode
imp = DatasetImport.create(
    dataset_id=dataset.id,
    records=[record],
    commit_mode='overwrite'
)

# Lookup record by ID and see the edited record
print(dataset.query().filter(_id=record['_id']))
```

### Upsert (Edit) Records

In order to only update (or add) specific field values in a dataset, users can utilize the upsert commit mode. Users will need to know the \_id of the records they wish to upsert, which can be retrieved by querying the dataset.

Similar to the example above, in the following example a few records will be imported and then edited:


```Python
from quartzbio import Dataset
from quartzbio import DatasetImport

dataset = Dataset.get_or_create_by_full_path('~/python_examples/upsert_records')

# Initial Import
imp = DatasetImport.create(
    dataset_id=dataset.id,
    records=[
        {'name': 'Francis Crick', 'birth_year': '1916'},
        {'name': 'James Watson', 'birth_year': '1928'},
        {'name': 'Rosalind Franklin', 'birth_year': '1920'}
    ]
)

# Retrieve the record to edit
record = dataset.query().filter(name='Francis Crick')[0]
# Change existing field
record['name'] = 'Francis Harry Compton Crick'
# Add a new field
record['birthplace'] = 'Northampton, England'

# Upsert mode
imp = DatasetImport.create(
    dataset_id=dataset.id,
    records=[record],
    commit_mode='upsert'
)

# Lookup record by ID and see the edited record
print(dataset.query().filter(_id=record['_id']))
```

### Delete Records

In order to completely delete a record from a dataset, users may use the delete commit mode and pass a list of record IDs (from their \_id field).

Users can delete records via an import if they have a file or list of record IDs or via a migration if they are deleting the results of a dataset query.

The following provides an example of Delete via Import:


```Python
from quartzbio import Dataset
from quartzbio import DatasetImport

dataset = Dataset.get_or_create_by_full_path('~/python_examples/data_delete')

# Initial Import
imp = DatasetImport.create(
    dataset_id=dataset.id,
    records=[
        {'name': 'six'},
        {'name': 'seven'},
        {'name': 'eight'},
        {'name': 'nine'}
    ]
)

for r in dataset.query(fields=['name']):
    print(r)
# {'name': 'six'}
# {'name': 'seven'}
# {'name': 'eight'}
# {'name': 'nine'}

# Get the record ID for 'nine'
record = dataset.query(fields=['_id']).filter(name='nine')

# Delete the record
imp = DatasetImport.create(
    dataset_id=dataset.id,
    records=list(record),
    commit_mode='delete'
)

# Why was six afraid of seven?
for r in dataset.query(fields=['name']):
    print(r)
# {'name': 'six'}
# {'name': 'seven'}
# {'name': 'eight'}
```

The following provides an example of Delete via Migration:


```Python
from quartzbio import Dataset
from quartzbio import DatasetImport

dataset = Dataset.get_or_create_by_full_path('~/python_examples/data_delete_migration')

# Initial Import
imp = DatasetImport.create(
    dataset_id=dataset.id,
    records=[
        {'name': 'Alice'},
        {'name': 'Bob'},
        {'name': 'Carol'},
        {'name': 'Chuck'},
        {'name': 'Craig'},
        {'name': 'Dan'},
        {'name': 'Eve'}
    ]
)

# Get the records where names begin with C
query = dataset.query().filter(name__prefix='C')

# Use migration shortcut to Delete
migration = query.migrate(dataset, commit_mode="delete")

# The above shortcut is equivalent to:
# migration = DatasetMigration.create(
#    source_id=dataset.id,
#    target_id=dataset.id,
#    commit_mode="delete",
#    source_params=dict(filters=[('name__prefix', 'C')])
# )

for r in dataset.query():
    print(r)

# {'name': 'Alice'},
# {'name': 'Bob'},
# {'name': 'Dan'},
# {'name': 'Eve'}
```