# Querying Datasets and Files

## Overview

The EDP is designed for easy access to molecular information. It provides an easy-to-use, real-time API for querying any dataset or file on the platform through the EDP Python or R client libraries. Users can also use Bash to query datasets. Users can also apply complex filters when querying datasets and files; to learn more about using filters, users can refer to the [Filters](https://quartzbio.github.io/quartzbio-python/filters.html#overview) documentation.

## Querying Datasets

Dataset query results are returned in pages, similar to a search engine. To narrow down search results, datasets can be filtered on one or more fields. Users can either build queries using a programming language (or even write raw JSON) or by building them directly on any dataset page in the EDP web application. The easiest way to query datasets is by using the EDP Python or R client libraries. 

A basic query returns a page of results from the specified public dataset. Users can set the paginate parameter to True to retrieve all records or use the limit parameter to specify how many records to retrieve. Users should note that in the R client, the limit parameter allows users to retrieve a maximum of 10,000 records in a single request. Additionally, the query function accepts the following parameters:

|    Parameter    |  Value  |                                                                                                                                  Description                                                                                                                                   |
|-----------------|---------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|     filters     | objects |                                                                                                                             A valid filter object.                                                                                                                             |
|     facets      | objects |                                                                                                                             A valid facets object                                                                                                                              |
|     fields      | string  |                                                                                                                  A list of fields to include in the results.                                                                                                                   |
| exclude\_fields | string  |                                                                                                                  A list of fields to exclude in the results.                                                                                                                   |
|    ordering     | string  |                                                                                                                     A list of fields to order results by.                                                                                                                      |
|      query      | string  |                                                                                                                             A valid query string.                                                                                                                              |
|      limit      | integer |                                                                                                                   The number of results to return per-page.                                                                                                                    |
|     offset      | integer |                                                                                                                      The record offset in the result-set.                                                                                                                      |
|    paginate     | boolean |                                                                                                                If True, returns all records. Default is False.                                                                                                                 |
|   page\_size    | integer | The internal batch size per request. Default is 100, with a maximum size of 10,000. Increasing the page\_size can increase the speed of the query, but large numbers can in some cases cause requests to fail due to the large amount of data coming out in a single response. |
| output\_format  | string  |                                                                                                  The output format of the query ('csv', 'tsv', or 'json'). Default is 'json'.                                                                                                  |

In Python:
```Python
# Users can set how many records they want to retrieve with the "limit" parameter
Dataset.get_by_full_path('quartzbio:Public:/ClinVar/5.2.0-20210110/Variants-GRCH37').query(limit=1000)

# Users can order query results using the ordering argument

# Order the query results by clinical_significance ascending 
Dataset.get_by_full_path('quartzbio:Public:/ClinVar/5.2.0-20210110/Variants-GRCH37').query(ordering='clinical_significance')

# Order the query results by clinical_significance descending 
Dataset.get_by_full_path('quartzbio:Public:/ClinVar/5.2.0-20210110/Variants-GRCH37').query(ordering='-clinical_significance')

# Query results can be ordered by multiple columns 

# Order the query results by clinical_significance descending and gene_symbol ascending 
Dataset.get_by_full_path('quartzbio:Public:/ClinVar/5.2.0-20210110/Variants-GRCH37').query(ordering=['-clinical_significance', 'gene'])
```

## Saving Queries

Dataset queries can be saved and then used to make queries on datasets with a similar structure. Saved queries can be created for any dataset and can be shared with members of a user's organization.

For example, users may save a query for a set of interesting genes. They can then make this query available for all datasets that contain genes. If shared with other users in the organization, they will also be able to apply this query.

The Saved Queries API

To retrieve Saved Queries that apply to a dataset, or all those available:

In Python:
```Python
dataset_queries = SavedQuery.all(dataset="<DATASET_ID>")

all_saved_queries = SavedQuery.all()
```

To use a saved query, users can retrieve the SavedQuery object and then apply the parameters.

In Python:
```Python
saved_query = SavedQuery.retrieve("SAVED_QUERY_ID")

# Option 1: from the SavedQuery instance (Python only)
results = saved_query.query("<DATASET_ID>")

# Option 2: from the Dataset.query() function
results = Dataset.retrieve("<DATASET_ID").query(**saved_query.params)
```

To create a SavedQuery, users can define the query parameters and provide a valid dataset, as well as give it a name and description.

In Python:

```Python
params = {
    "entities": [["gene", "MTOR"], ["gene", "BRCA2"], ["gene", "CFTR"]]
}

saved_query = SavedQuery.create(
    name="Interesting Genes",
    description="Interesting genes as defined in Pubmed article 512312"
    dataset="<DATASET_ID>",
    params=params
)
```

### Using Saved Queries 

Saved queries can be used via the EDP API or the web UI. The UI will only display queries compatible with the current dataset. This compatibility check is handled automatically by the platform.

When viewing a dataset in the web UI, previously saved queries can be retrieved by selecting "Load Filters" and then selecting one. Users can save a new query by applying filters to the dataset and then by clicking "Save Filters." For more information, users can refer to the [Dataset Exploration](https://quartzbio.freshdesk.com/en/support/solutions/articles/73000597740) documentation.

## Querying Files

File objects can be queried and filtered on one or more fields. The query results are returned in pages. It is important to note that text files such as CSV, TXT, TSV, or BED must be uploaded with headers; otherwise, the query will return incorrect results because the query logic considers the first row from the file as the header.

A basic query returns a page of results from the specified file object:

In Python:
```Python
clinvar = Object.get_by_full_path('quartzbio:Public:/ClinVar/5.2.0-20210110/ClinVar-5-2-0-20210110-Variants-GRCH37-1425664822266145048-20221110194518.json.gz')
clinvar.query()
```

Users can retrieve a specified number of records from the file by setting the limit query parameter:

In Python:
```Python
clinvar = Object.get_by_full_path('quartzbio:Public:/ClinVar/5.2.0-20210110/ClinVar-5-2-0-20210110-Variants-GRCH37-1425664822266145048-20221110194518.json.gz')
q = clinvar.query(limit=50)
```

All fields from the file can be retrieved by calling the fields method:

In Python:
```Python
fields = Object.get_by_full_path('quartzbio:Public:/ClinVar/5.2.0-20210110/ClinVar-5-2-0-20210110-Variants-GRCH37-1425664822266145048-20221110194518.json.gz').query().fields()
```

Users can also use the download\_url() method to load files into readers such as pandas:

In Python:
```Python
from quartzbio import *
import pandas

# Get file using ID or full path
f = Object.retrieve("ID")
f = Object.get_by_full_path("vault/path/to/file.csv")

# Get file download URL and load into reader
url = f.download_url()
pandas.read_csv(url)
```

## Supported File Extensions and Compressions

File querying is only supported for the following file extensions and compressions:

| **File Extensions** | **Compression** |
|-----------------|-------------|
|       txt       | GZIP, BZIP2 |
|       csv       | GZIP, BZIP2 |
|       tsv       | GZIP, BZIP2 |
|       bed       | GZIP, BZIP2 |
|      json       | GZIP, BZIP2 |
|     parquet     |    GZIP     |

The only supported encoding is UTF-8.

The output format of the query can be provided by using the output\_format parameter which can be one of the following:

| **Output Format**  |                       **Description**                        |
|----------------|----------------------------------------------------------|
| json (default) |            applicable to all file extensions             |
|      csv       | applicable only to **csv**, **txt**, **tsv**, or **bed** file extensions |
|      tsv       | applicable only to **csv**, **txt**, **tsv**, or **bed** file extensions |

Example:

In Python:
```Python
clinvar = Object.get_by_full_path('quartzbio:Public:/ClinVar/5.2.0-20210110/ClinVar-5-2-0-20210110-Variants-GRCH37-1425664822266145048-20221110194518.json.gz')
clinvar.query(output_format='json')
```

## API Endpoints

Methods do not accept URL parameters or request bodies unless specified. Please note that if your EDP endpoint is sponsor.edp.aws.quartz.bio, you would use sponsor.api.edp.aws.quartz.bio.

Dataset Query

| Method |             HTTP Request              |   Description    |                                     Authorization                                     |                         Response                          |
|--------|---------------------------------------|------------------|---------------------------------------------------------------------------------------|-----------------------------------------------------------|
| query  | POST /v2/datasets/{DATASET\_ID}/query | Query a dataset. | This request requires an authorized user with permission to query the target dataset. | The dataset query response has a structure defined below. |

Request Body:

The request body should contain valid query parameters:

|    Property     |  Value  |                 Description                 |
|-----------------|---------|---------------------------------------------|
|     filters     | objects |           A valid filter object.            |
|     facets      | objects |            A valid facets object            |
|     fields      | string  | A list of fields to include in the results. |
| exclude\_fields | string  | A list of fields to exclude in the results. |
|    ordering     | string  |    A list of fields to order results by.    |
|      query      | string  |            A valid query string.            |
|      limit      | integer |  The number of results to return per-page.  |
|     offset      | integer |    The record offset in the result-set.     |

Users can refer to the [Filters documentation](https://quartzbio.github.io/quartzbio-python/filters.html) for more information about constructing filters.

The dataset query response has the following structure:

|  Property   |  Value  |                   Description                   |
|-------------|---------|-------------------------------------------------|
|   dataset   | string  |            The name of the dataset.             |
| dataset\_id | integer |             The ID of the dataset.              |
|   facets    | objects |   Facet results (if a facets are requested).    |
|   offset    | integer | The current offset within the whole result-set. |
|   results   | objects |           A list of dataset records.            |
|    took     | integer |  Time to retrieve the records, in miliseconds.  |
|    total    | integer | The total number of records in the result-set.  |

Saved Queries

| Method |                   HTTP Request                    |       Description       |                       Authorization                       |                   Response                   |
|--------|---------------------------------------------------|-------------------------|-----------------------------------------------------------|----------------------------------------------|
|  get   | GET https://<EDP\_API\_HOST>/v2/saved\_queries/{ID} | Retrieve a Saved Query. | This request requires an authorized user with permission. | The response contains a SavedQuery resource. |

| Method |                 HTTP Request                  |        Description        |                             Authorization                              |                      Response                      |
|--------|-----------------------------------------------|---------------------------|------------------------------------------------------------------------|----------------------------------------------------|
| create | POST https://<EDP\_API\_HOST>/v2/saved\_queries | Create a new Saved Query. | This request requires an authorized user with appropriate permissions. | The response contains the new SavedQuery resource. |

Request Body:

|  Property   |  Value  |                                                                 Description                                                                 |
|-------------|---------|---------------------------------------------------------------------------------------------------------------------------------------------|
|    name     | string  |                                                      A short name for the Saved Query.                                                      |
| description | string  |                                                     A description for the Saved Query.                                                      |
|   dataset   | string  | The ID or full\_path of a dataset to validate this query parameters against. This is needed on initial creation to ensure valid parameters. |
|   params    | objects |                                     The query parameters (see query parameters above for _query_ method).                                     |
| is\_shared  | boolean |                                  If True, this query will be shared with other members of you organization                                  |

| Method |                     HTTP Request                     |      Description      |                                  Authorization                                   |                      Response                       |
|--------|------------------------------------------------------|-----------------------|----------------------------------------------------------------------------------|-----------------------------------------------------|
| delete | DELETE https://<EDP\_API\_HOST>/v2/saved\_queries/{ID} | Delete a Saved Query. | This request requires an authorized user with write permissions on the resource. | The response returns "HTTP 200 OK" when successful. |

| Method |                 HTTP Request                 |                   Description                    |               Authorization               |                       Response                        |
|--------|----------------------------------------------|--------------------------------------------------|-------------------------------------------|-------------------------------------------------------|
|  list  | GET https://<EDP\_API\_HOST>/v2/saved\_queries | Retrieves all Saved Queries available to a user. | This request requires an authorized user. | The response contains a list of SavedQuery resources. |

