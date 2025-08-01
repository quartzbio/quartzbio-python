# Importing Data via API

## Overview

The EDP specializes in harmonizing a variety of data sources through its robust import system. Importing data is the process of converting a flat file into a dataset that can be queried in real time. The EDP supports data in the most common formats, including JSONL, VCF, CSV, TSV, XML, GTF, and GFF3. Users can contact QuartzBio Support for assistance with importing many other formats (including custom, proprietary formats, and unstructured data).

The EDP's import system automates the traditional ETL (Extract, Transform, Load) process. The process typically starts by uploading files into a vault. An import task can then be configured and launched. The import system automatically handles data extraction (file parsing), data transformation, data validation, and finally data loading. Users can refer to the Import Parameters documentation for more information about configuring optional parameters for data parsing, entity detection, validation, and annotation.

## Supported Formats

Users should note that only UTF-8 encoded files are supported. Content may be corrupted during the import process if non-UTF-8 files are imported.

The following file formats and extensions are supported:

|                       Name                        | File Extension | Previewable in EDP? | Transformable into a Dataset? |
|---------------------------------------------------|----------------|---------------------|-------------------------------|
|              Comma Separated Values               |      .csv      |          Y          |               Y               |
|              General Feature Format               |    .gff3.gz    |          Y          |               Y               |
|               Gene Transfer Format                |      .gtf      |          Y          |               Y               |
|            Hyper Text Markup Language             |     .html      |          Y          |               N               |
| JavaScript Object Notation (in JSON Lines format) |     .json      |          Y          |               Y               |
|            Mutation Annotation Format             |      .maf      |          Y          |               Y               |
|             Portable Document Format              |      .pdf      |          Y          |               N               |
|               Tab Separated Values                |      .tsv      |          Y          |               Y               |
|               Unformatted text file               |      .txt      |          Y          |               Y               |
|                Variant Call Format                |      .vcf      |          Y          |               Y               |
|            Extensible Markup Language             |      .xml      |          Y          |   Y (requires  a template)    |
|                       Excel                       |   .xlsx/.xsl   |          Y          |               Y               |

## Reader Parameters

EDP automatically detects the file format based on the extension, except for the Nirvana JSON file, and parses the file using a specialized "reader". It is possible to manually specify a reader and modify reader parameters using the [reader\_params](https://quartzbio.freshdesk.com/en/support/solutions/articles/73000629949) attribute of the DatasetImport resource. 

| Reader  |   Reader name  |    Extension     |
|---------|----------------|------------------|
|   VCF   |      vcf       |       .vcf       |
|  JSONL  |      json      |      .json       |
|   CSV   |      csv       |       .csv       |
|   TSV   |      tsv       | .tsv, .txt, .maf |
|   XML   |      XML       |       .xml       |
|   GTF   |      gft       |       .gtf       |
|  GFF3   |      gff3      |      .gff3       |
| Nirvana |      json      |  nirvana .json   |
|  Excel  |      xlsx      |      .xlsx       |
|  Excel  |      xls       |                  |

EDP supports GZip compression for all file types. Gzipped files must have the .gz file extension in addition to their format extension (i.e. file.vcf.gz). Users are recommended to compress files with GZip for faster uploads and imports.

## Importing from Files

The first step to getting data onto EDP is by uploading files into a vault. Users can refer to the [Vaults documentation](https://quartzbio.freshdesk.com/en/support/solutions/articles/73000598224) for more information.

In Python:
```Python
from quartzbio import Vaultfrom quartzbio import Object# Upload a local file to the root of the personal Vaultvault = Vault.get_personal_vault()uploaded_file = vault.upload_file('local/path/file.vcf.gz', '/')# Retrieve the file by its full path:uploaded_file = Object.get_by_full_path('~/file.vcf.gz')
```

Once the files have been uploaded, they can be imported into any new or existing dataset ([Learn how to create a dataset](https://quartzbio.freshdesk.com/en/support/solutions/articles/73000613900)). To launch an import, users can utilize the DatasetImport method. The user will need to provide the uploaded file and target dataset as inputs. Once the import has been launched, it is possible to track the progress through the API on the web interface through the Activity tab.

In Python:
```Python
from quartzbio import Dataset
from quartzbio import DatasetImport

dataset = Dataset.get_or_create_by_full_path('~/python_examples/test_dataset')

# Launch the import
imp = DatasetImport.create(
    dataset_id=dataset.id,
    object_id=uploaded_file.id,
    commit_mode='append'
)

# Follow the import status
dataset.activity(follow=True)
```

## Importing from URLs

If the files are on a remote server and accessible by URL, they can be imported using a manifest. A manifest is simply a list of files (URLs and other attributes) to import:

In Python:
```Python
from quartzbio import Manifest

source_url = "https://s3.amazonaws.com/downloads.quartzbio.com/demo/interesting-variants.json.gz"

manifest = Manifest()
manifest.add_url(source_url)
```

Once the manifest has been created, it can be imported into any new or existing dataset. To launch an import, users can employ the DatasetImport resource, providing the manifest and target dataset as input. Once the import has been launched it is available to track the progress through the API or on the web. 

In Python:

```Python
from quartzbio import Dataset
from quartzbio import DatasetImport

dataset = Dataset.get_or_create_by_full_path('~/python_examples/manifest_dataset')

# Launch the import
imp = DatasetImport.create(
    dataset_id=dataset.id,
    manifest=manifest.manifest,
    commit_mode='append'
)

# Follow the import status
dataset.activity(follow=True)
```

The EDP can also pull data from DNAnexus, SevenBridges, and many other pipelines. [](https://quartzbio.freshdesk.com/en/support/solutions/articles/73000608614)Users can contact QuartzBio Support for more information.

## Importing from Records

The EDP can also import data as a list of records, i.e. a list of Python dictionaries or R data. Users should note that the EDP supports only importing up to 5000 records at a time through this method. Importing from records is most optimal for importing small datasets and making edits to datasets. For larger imports and transforms, users are recommended to import from compressed JSONL files.

In Python:

```Python
from quartzbio import DatasetImport

records = [
    {'gene': 'CFTR', 'importance': 1, 'sample_count': 2104},
    {'gene': 'BRCA1', 'importance': 1, 'sample_count': 1391},
    {'gene': 'CLIC2', 'importance': 5, 'sample_count': 14},
]
dataset = Dataset.get_or_create_by_full_path('~/python_examples/records_dataset')
imp = DatasetImport.create(
    dataset_id=dataset.id,
    data_records=records
)
```

## Command Line Tools

Users can import data files using the quartzbio import command from the quartzbio Python module:
```
# Import a file (create the dataset if necessary):
quartzbio import --create-dataset --follow ~/test-dataset data.vcf.gz

# Import files in upsert mode (create the dataset from a template if necessary):
quartzbio import --create-dataset --template-file template.json --commit-mode=upsert --follow ~/test-dataset data.vcf.gz
```

Users can create a dataset template file (e.g. template.json) to be used during file import:
```
{
  "name": "Example EDP Dataset template",
  "fields": [
    {
      "name": "gene_symbol",
      "description": "HUGO gene symbol",
      "entity_type": "gene",
      "data_type": "string"
    },
    {
      "name": "variant",
      "entity_type": "variant",
      "data_type": "string"
    }
  ]
}
```

An easy way to upload files to a vault in batches is to use the quartzbio upload command: 

```
# Upload local_folder to the root of the personal vault:
quartzbio upload ./local_folder
```

If multiple files are uploaded, the command will cross-check the files and upload only the missing files and folders. Users should note that comparison is performed by filename, not by file contents. Users can refer to the [Vaults and Objects](https://quartzbio.freshdesk.com/en/support/solutions/articles/73000615717) documentation for more information about batch uploading. 

## Transforming Imported Data

Imported data can be transformed (fields added or edited) by providing a list of fields to the target\_fields parameter. [Expressions](https://quartzbio.freshdesk.com/en/support/solutions/articles/73000606023) can be used to dynamically modify the data as it is imported, making it possible to

-   Modify data types (numbers to strings or vice-versa)
-   Add new fields with static or dynamic content
-   Format strings and dates to clean the data
-   Merge data from datasets

The following example imports a list of records and transforms the contents in a single step:

In Python:
```Python
from quartzbio import Dataset
from quartzbio import DatasetImport

dataset = Dataset.get_or_create_by_full_path('~/python_examples/transform_import')

# The original records
records = [
    {'name': 'Francis Crick'},
    {'name': 'James Watson'},
    {'name': 'Rosalind Franklin'}
]

# The transforms to apply through "target_fields"
# Compute the first and last names.
target_fields = [
    {
        "name": "first_name",
        "description": "Adds a first name column based on name column",
        "data_type": "string",
        "expression": "record.name.split(' ')[0]"
    },
    {
        "name": "last_name",
        "description": "Adds a last name column based on name column",
        "data_type": "string",
        "expression": "record.name.split(' ')[-1]"
    }
]

imp = DatasetImport.create(
    dataset_id=dataset.id,
    data_records=records,
    target_fields=target_fields
)

# Wait until the import finishes
dataset.activity(follow=True)

for record in dataset.query(exclude_fields=['_id', '_commit']):
    print record

# Output:
# {'first_name': 'Francis', 'last_name': 'Crick', 'name': 'Francis Crick'}
# {'first_name': 'James', 'last_name': 'Watson', 'name': 'James Watson'}
# {'first_name': 'Rosalind', 'last_name': 'Franklin', 'name': 'Rosalind Franklin'}
```


Existing imported data can also be modified by using migrations. This allows a user to add a column, modify data within a column, or remove a column.

## Validating Imported Data

When importing data, every record is validated to ensure it can be committed into a Dataset. Validation compares the schema of existing Dataset fields with the values of incoming data and issues validation errors if the Dataset field schema does not match the incoming value. Validation can also issue warnings.

During validation, a field's data\_type and is\_list values are checked. All records are evaluated (although users may override this to fail fast on the first error). A commit will not be created if there are any validation errors.

The following settings can be passed to the [validation\_params](https://quartzbio.freshdesk.com/en/support/solutions/articles/73000629949) field.

-   disable - (boolean) default False - Disables validation completely
-   raise\_on\_errors - (boolean) default False - Will fail the import on first validation error encountered.
-   strict\_validation - (boolean) default False - Will upgrade all validation warnings to errors.
-   allow\_new\_fields - (boolean) default False - If strict validation is True, will still allow new fields to be added

The following example fails an import as soon as invalid data is detected:

In Python:

```Python
imp = DatasetImport.create(
    dataset_id=dataset.id,
    object_id=object.id,
    validation_params={
        'raise_on_errors': True
    }
)
```

The following example disables validation from running, which can improve import performance.

In Python:

```Python
imp = DatasetImport.create(
    dataset_id=dataset.id,
    object_id=object.id,
    validation_params={
        'disable': True
    }
)
```

## Committing Imported Data

Once data has been extracted from files, transformed, and validated, it will be automatically indexed ("committed") into EDP's datastore. Dataset commits represent all changes made to the target dataset by the import process. Four commit modes can be selected depending on the scenario: append (default), overwrite, upsert, and delete. The commit mode can be specified when creating the DatasetImport using the commit\_mode parameter.

append (default)

Append mode always adds records to the dataset. Imported record IDs (the \_id field) will be overwritten with unique values. **Only append commits can be rolled back at this time.**

overwrite

Overwrite mode requires that each record have a value in the \_id field. Existing records with the same \_id are overwritten completely.

upsert

Upsert mode merges imported records with existing records, based on the value of their \_id field. Object fields are merged, scalar fields (such as integers and strings) are overwritten, and new fields are added. **List fields are completely overwritten regardless of the data type.**

delete

Delete mode is a special case that deletes existing dataset records based on their \_id field.

## Performance Tips

Below are some tips for improving the performance of dataset imports.

**Disable Data validation**

Data validation is enabled by default when running imports or migrations. This is used for data type checking on each record that is processed. Disabling this will provide a per-record performance improvement, translating to substantial time savings for large datasets.

**Dataset Capacity**

For many simultaneous imports, use a larger dataset capacity. Simultaneous imports have a high upper limit (50+) but simultaneous commits are throttled. Every import spawns a commit that does the actual indexing of the data. small capacity datasets allow a single running commit per dataset at a time, the medium allows 2 simultaneous commits, and large allows 3 simultaneous commits. Commits will remain queued until running ones are completed.

Indexing operations and query operations are also faster for larger-capacity datasets. If it is expected a dataset to be queried at high frequency, then we recommend using a larger dataset. If the dataset already exists, copy the dataset into a medium or large dataset.

**Optimize "expensive" Expressions**

Some dataset field expressions are more expensive than others. Dataset query expressions can be sped up by applying exact filters, using fields to only pull back the fields that are needed, or using dataset\_count() if the length is what is needed.

## API Endpoints

Methods do not accept URL parameters or request bodies unless specified. Please note that if your EDP endpoint is sponsor.edp.aws.quartz.bio, you would use sponsor.api.edp.aws.quartz.bio.

Dataset Imports

| Method |                  HTTP Request                   |              Description               |                                 Authorization                                  |                                            Response                                             |
|--------|-------------------------------------------------|----------------------------------------|--------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| create | POST https://<EDP\_API\_HOST>/v2/dataset\_imports | Create a dataset import for a dataset. | This request requires an authorized user with write permission on the dataset. | The response returns "HTTP 201 Created", along with the DatasetImport resource when successful. |

Request Body:

In the request body, provide an object with the following properties:

|      Property      |  Value  |                                                      Description                                                      |
|--------------------|---------|-----------------------------------------------------------------------------------------------------------------------|
|    commit\_mode    | string  |                                                 A valid commit mode.                                                  |
|    dataset\_id     | integer |                                    (Optional) The ID of an existing object on EDP.                                    |
|     object\_id     | integer |                                        (Optional) A file manifest (see below).                                        |
|      manifest      | object  |                  (Optional) A vault location to store the export output (must be an EDP full path).                   |
|   data\_records    | objects |                                 (Optional) A list of records to import synchronously.                                 |
|    description     | string  |                                       (Optional) A description of this import.                                        |
|   entity\_params   | object  |                               (Optional) Configuration parameters for entity detection.                               |
|   reader\_params   | object  |                                   (Optional) Configuration parameters for readers.                                    |
| validation\_params | object  |                                  (Optional) Configuration parameters for validation.                                  |
| annotator\_params  | object  |                                (Optional) Configuration parameters for the Annotator.                                 |
|  include\_errors   | boolean | If True, a new field (\_errors) will be added to each record containing expression evaluation errors (default: True). |
|   target\_fields   | objects |                          A list of valid dataset fields to create or override in the import.                          |
|      priority      | integer |                                           A priority to assign to this task                                           |

When creating a new import, either manifest, object\_id or data\_records must be provided. Using a manifest allows you to import a remote file accessible by HTTP(S), for example:

```
# Example Manifest
{
    "files": [{
        "url": "https://example.com/file.json.gz",
        "name": "file.json.gz",
        "format": "json",
        "size": 100,
        "md5": "",
        "base64_md5": ""
    }]
}
```

Manifests can include the following parameters:

|      Property      | Value  |                                                          Description                                                          |
|--------------------|--------|-------------------------------------------------------------------------------------------------------------------------------|
|        url         | string |            A publicly accessible URL pointing to a file to import into EDP. You must pass a URL or an object\_id.             |
|     object\_id     |  long  |                          The ID of an existing object on EDP. You must pass an object\_id or a URL.                           |
|        name        | string |                   (Optional) The name of the file. If not passed, EDP will take it from the URL or object.                    |
|       format       | string |                (Optional) The file format of the file. If not passed, EDP will take it from the URL or object.                |
|        md5         | string | (Optional) The md5 hash of the file contents. If passed, EDP will validate the file after downloading and fail if mismatched. |
|   entity\_params   | object |                                   (Optional) Configuration parameters for entity detection.                                   |
|   reader\_params   | object |                                       (Optional) Configuration parameters for readers.                                        |
| validation\_params | object |                                     (Optional)  Configuration parameters for validation.                                      |

| Method |                      HTTP Request                      |       Description        |                                 Authorization                                  |                      Response                       |
|--------|--------------------------------------------------------|--------------------------|--------------------------------------------------------------------------------|-----------------------------------------------------|
| delete | DELETE https://<EDP\_API\_HOST>/v2/dataset\_imports/{ID} | Delete a dataset import. | This request requires an authorized user with write permission on the dataset. | The response returns "HTTP 200 OK" when successful. |

Deleting dataset imports is not recommended as data provenance will be lost.

| Method |                    HTTP Request                     |            Description             |                                 Authorization                                 |                    Response                     |
|--------|-----------------------------------------------------|------------------------------------|-------------------------------------------------------------------------------|-------------------------------------------------|
|  get   | GET https://<EDP\_API\_HOST>/v2/dataset\_imports/{ID} | Retrieve metadata about an import. | This request requires an authorized user with read permission on the dataset. | The response contains a DatasetImport resource. |

| Method |                         HTTP Request                         |                 Description                 |                                 Authorization                                 |                         Response                         |
|--------|--------------------------------------------------------------|---------------------------------------------|-------------------------------------------------------------------------------|----------------------------------------------------------|
|  list  | GET https://<EDP\_API\_HOST>/v2/datasets/{DATASET\_ID}/imports | List the imports associated with a dataset. | This request requires an authorized user with read permission on the dataset. | The response contains a list of DatasetImport resources. |

| Method |                       HTTP Request                        |       Description        |                                 Authorization                                  |                                   Response                                   |
|--------|-----------------------------------------------------------|--------------------------|--------------------------------------------------------------------------------|------------------------------------------------------------------------------|
| cancel | PUT https://<EDP\_API\_HOST>/v2/dataset\_imports/{IMPORT\_ID} | Cancel a dataset import. | This request requires an authorized user with write permission on the dataset. | The response will contain a DatasetImport resource with the status canceled. |

Request Body

In the request body, provide a valid DatasetResource object (see _create_ above) with status = canceled.
