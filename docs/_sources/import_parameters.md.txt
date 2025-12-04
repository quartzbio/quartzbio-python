# Import Parameters

## Overview

EDP's [import system](https://quartzbio.github.io/quartzbio-python/importing_data.html) accepts optional parameters for the Reader, [Entity Detection](https://quartzbio.github.io/quartzbio-python/import_parameters.html#entity-detection-parameters), Validation, and the Annotator.  

## Reader Parameters

The EDP will automatically select a reader based on the imported file's extension. This is not applicable to the Nirvana JSON file because it has the same extension as the JSONL file (.json), so the reader attribute has to be set manually to nirvana.

In the case where the extension is not recognized, users can manually select a reader using the reader attribute of [reader\_params](https://quartzbio.github.io/quartzbio-python/import_parameters.html#reader-parameters) by setting the associated reader name as its value:

```
# Force the JSONL reader
reader_params = {
    'reader': 'json'
}

imp = DatasetImport.create(
    reader_params=reader_params
    ...
)
```

# JSON (JSONL)

The JSONL format supported by EDP has four requirements (adapted from [jsonlines.org](http://jsonlines.org/)):

1\. **UTF-8 encoding**

JSON allows encoding Unicode strings with only ASCII escape sequences. However, those escapes will be hard to read when viewed in a text editor. The author of the JSON Lines file may choose to escape characters to work with plain ASCII files.

Non-ascii content may be corrupted during the import process if non-UTF-8 files are imported.

2\. **Each line must be a complete JSON object**

Specifically, each line must be a JSON object without any internal line-breaks. For example, here are three records:

```
{"field": 1}
{"field": 2}
{"field": 3}
```

3\. **Lines are separated by '\\n'**

This means '\\r\\n' is also supported because trailing white space is ignored when parsing JSON values.

The last character in the file may be a line separator, and it will be treated the same as if there was no line separator present.

4\. **The file extension must be .json or .json.gz**

JSON Lines files for EDP `must be saved with the .json extension`. Files may be gzipped, resulting in the .json.gz extension.

**CSV/TSV**

The following parameters can be passed for files that end with extension .csv, .tsv, and .txt.

-   delimiter: A one-character string used to separate fields. Defaults to ',' for CSVs and '\\t' for TSVs and TXT files
-   quotechar: A one-character string used to quote fields containing special characters, such as the delimiter or quotechar, or which contain new-line characters. It defaults to '"'.
-   header: The row number (starting from 0) containing the header, None (to indicate no header), or infer (default). By default, column names are inferred from the first row unless headercols are provided, in which case the file is assumed to have no header row. Set header = 0 and provide headercols to replace existing headers.
-   headercols: A list of field names that represent column headers. By default, providing headercols assumes the file has no header. To replace existing headers, set header = 0). The order of the columns matters and must match the number of delimited columns in each line.
-   comment: A string used to determine which lines in the files are comments. Lines that begin with this string will be ignored. Default is '#'.
-   skiprows: A list of integers that define the line numbers of the file that should be skipped. The first line is line 0. Default is \[\].
-   skipcols: A list of integers that define the columns of the file that should be ignored. The first column is column 0. Default is \[\].

**Column Ordering:**

This reader will preserve the column order of the original file, unless otherwise overridden with an import template.

**Numeric Fields:**

This reader will cast all numeric fields to doubles.

The following example modifies the default CSV reader to handle a pipe-delimited file with 5 header rows:

```
# Custom reader params for a pipe-delimited "CSV" file with 5 header rows:
csv_reader_settings = {
    'delimiter': '|',
    'skiprows': [0, 1, 2, 3, 4]
}

imp = DatasetImport.create(
    reader_params=csv_reader_settings
    ...
)
```

**Excel**

The following parameters can be passed for files that end with extension .xlsx and .xsl:

-   sheet\_name: Specifies the sheet to be imported into the dataset. Can be string or int. Default is 0 (first sheet). 
    -   Strings are used for sheet names, and integers are used in zero-indexed sheet positions.
    -   Only one sheet can be imported into a dataset.
-   header: An integer that specifies the row (0-indexed) to use for the column labels of the dataset. Default is 0 (first row). Specify None if there is no header.
-   names: A list of column names to use. If using, specify header=None.
-   usecols: Specifies columns to import into dataset. Default is None (all columns). 
    -   Can specify columns by entering list of column numbers to be imported (0-indexed).
    -   Can specify columns by entering list of column names.
    -   Can specify columns by entering string of comma separated list of Excel column letters and column ranges (e.g. “A:E” or “A,C,E:F”). Ranges are inclusive of both sides.
-   dtype: Specifies data type of data or columns. Default is None (data type for each column is inferred based on data). 
    -   Can specify data type for all data by entering data type string. Enter "object" to preserve data as stored in Excel and not interpret dtype.
    -   Can specify data type of each column by entering dict of column:type.
-   skiprows: Specifies row or rows to be skipped in the data import.
    -   Can specify list of row numbers (0-indexed) to skip.
    -   Can specify number of lines to skip (int) at the start of the file. E.g skiprows=1 will skip first row.
    -   Can specify callable function to be evaluated against row indices, returning True if the row should be skipped and False otherwise. E.g an example callable argument is "lambda x: x in \[0, 2\]".
-   nrows: Specifies number of rows to import from the start of the file. 
-   na\_values: Additional strings to recognize as NA/NaN. Can be str, list of strings, or dict. Default is None.
    -   If dict passed, specify per-column NA values.
    -   By default the following values are interpreted as NaN: ‘’, ‘#N/A’, ‘#N/A N/A’, ‘#NA’, ‘-1.#IND’, ‘-1.#QNAN’, ‘-NaN’, ‘-nan’, ‘1.#IND’, ‘1.#QNAN’, ‘<NA>’, ‘N/A’, ‘NA’, ‘NULL’, ‘NaN’, ‘None’, ‘n/a’, ‘nan’, ‘null’.
-   keep\_default\_na: Boolean. Whether or not to include the default NaN values when parsing the data. Default is True.
-   na\_filter: Boolean. Whether to detect missing value markers (empty strings and the value of na\_values). Default is True.
    -   In data without any NAs, passing na\_filter=False can improve the performance of reading a large file.

**VCF**

The following parameters can be passed for files that end with extension .vcf.

-   genome\_build: The string 'GRCh37' or 'GRCh38'. If no genome\_build is passed an attempt to guess the build will be made from the file headers and will fallback to GRCh37 if nothing is found.
-   explode\_annotations: Default: False - Will explode the annotations column of the VCF by creating one new record per annotation. By default it will look for annotations at the ANN column within the info object (info.ANN). This key can be configured with the annotations\_key parameter.
-   annotations\_key: The field name that contains the VCF annotations. For use with explode\_annotations parameter. The default key is ANN.
-   sample\_key: The field name that the VCF parser will output the VCF samples to. The default key is sample.

**XML**

The following parameters can be passed for files that end with extension .xml.

-   item\_depth: An integer that defines at which XML element to begin record enumeration. Default is 1. A depth of 0 would be the XML document root element and would return a single record.
-   required\_keys: A list of strings that represent items that must exist in the XML element. Otherwise the record will be ignored.
-   cdata\_key: A string that identifies the text value of a node element. Default is text
-   attr\_prefix: A string representing the default prefix for node attributes. Default is @

Example XML Document:
```xml
<xml>
    <library>
        <shelf>
            <book lang="eng">
                <title>EDP Docs, 3rd Edition</title>
                <publish_date></publish_date>
                <summary></summary>
            </book>
            <book lang="eng">
                <title></title>
                <publish_date></publish_date>
                <summary></summary>
            </book>
        </shelf>
        <shelf>
            <book>
                <title></title>
            </book>
        </shelf>
    </library>
</xml>
```

For the above example:

-   item\_depth=0 would parse a single library record with nested shelves and books. 
    -   item\_depth=1 would parse two shelf records with nested books. 
    -   item\_depth=2 would parse three book records.
-   required\_keys=\[\] would return 3 book records
    -   required\_keys=\['title'\] would also return 3 book records 
    -   required\_keys=\['summary'\] would return only 2 book records
-   cdata\_key="value" would return the field name book.title.value
-   attr\_prefix="" would return the field name book.lang attr\_prefix="\_" would return the field name book.\_lang

Example XML Document:

```
<xml>
    <library>
        <shelf>
            <book></book>
        </shelf>
        <shelf>
            <dust></dust>
        </shelf>
    </library>
</xml>
```

For the above example:

-   item\_depth=1 and required\_keys=\['dust'\] would parse 1 shelf record.

**GFF3**

The following parameters can be passed for files that end with extension .gff3.

-   comment: A string used to determine which lines in the files are comments. Lines that begin with this string will be ignored. Default is '##'.

**Nirvana JSON**

The Nirvana JSON format supported by EDP has to meet the [official Illumina's Nirvana JSON layout](https://illumina.github.io/NirvanaDocumentation/file-formats/nirvana-json-file-format/) in order to be parsed properly.

## Entity Detection Parameters

When importing data, every field is sampled and to determine if it is an EDP entity. The following configuration parameters allow for customization of this detection by setting [entity\_params](https://quartzbio.github.io/quartzbio-python/import_parameters.html#entity-detection-parameters) on the import object.

Genes and variants are detected by default. The example below overrides this and attempts to detect only genes and literature entities:

```Python
imp = DatasetImport.create(
    dataset_id=dataset.id,
    object_id=object.id,
    entity_params={
        'entity_types': ['gene', 'literature']
    }
)
```

To completely disable entity detection, users can set the disable attribute

```Python
imp = DatasetImport.create(
    dataset_id=dataset.id,
    object_id=object.id,
    entity_params={
        'disable': True
    }
)
```

### Validation Parameters

The following settings can be passed to the `validation_params` field.

-   disable - (boolean) default False - Disables validation completely
-   raise\_on\_errors - (boolean) default False - Will fail the import on first validation error encountered.
-   strict\_validation - (boolean) default False - Will upgrade all validation warnings to errors.
-   allow\_new\_fields - (boolean) default False - If strict validation is True, will still allow new fields to be added

Validation will raise the following errors and warnings. The list below represents them in the following format: \[Error code\] Name - Description

**Warnings:**

-   \[202\] Column Name Warning: Column name uses characters that do not comply with strict column name validation. (upgraded to an Error if strict\_validation=True)
-   \[203\] New Column added: A new column was added to the Dataset (upgraded to an Error if strict\_validation=True and allow\_new\_fields=False)
-   \[302\] List Expected violation: A column expected a list of values but didn't receive them. For example, a field has is\_list=True but received a single string (upgraded to an Error if strict\_validation=True)
-   \[303\] Unexpected List violation: A column expected a single value but received a list of values. For example a field has is\_list=False but received a list of strings. (upgraded to an Error if strict\_validation=True)
-   \[400\] Too Many Columns in record: Warns if 150 or more columns are found. Errors if 400 or more.

**Errors:**

-   \[301\] Invalid Value for Field: Value is not a valid type (e.g. An integer passed for a date field data\_type)
-   \[304\] NaN Value for Field: Value is a JSON "NaN" value which can not be indexed by EDP.
-   \[305\] Infinity Value for Field: Value is a JSON "Infinity" value which can not be indexed by EDP.
-   \[306\] Max String Length for Field: The max value for the string data\_type is 32,766 bytes. Anything larger must be a text data\_type.

### Annotator Parameters

The following settings can be used to customize the annotator that is used during transformation with the `annotator_params` attribute.

-   annotator - (string) Choose from "simple" (default), "serial", or "parallel".  
    

Methods do not accept URL parameters or request bodies unless specified. Please note that if your EDP endpoint is sponsor-cloud.edp.aws.quartz.bio, you would use sponsor-cloud.api.edp.aws.quartz.bio.
For correct work of the API, you need to change `<EDP_API_HOST>` to your current domain, such as my-domain.api.edp.aws.quartz.bio

**Deleting dataset imports is not recommended as data provenance will be lost.**

| Method |                         HTTP Request                         |                                  Authorization                                  |                         Response                         |
|--------|--------------------------------------------------------------|---------------------------------------------------------------------------------|----------------------------------------------------------|
| delete |    DELETE https://<EDP\_API\_HOST>/v2/dataset\_imports/{ID}    | This request requires an authorized user with write permissions on the dataset. |   The response returns "HTTP 200 OK" when successful.    |
|  get   |     GET https://<EDP\_API\_HOST>/v2/dataset\_imports/{ID}      | This request requires an authorized user with write permissions on the dataset. |   The response returns "HTTP 200 OK" when successful.    |
|  list  | GET https://<EDP\_API\_HOST>/v2/datasets/{DATASET\_ID}/imports |  This request requires an authorized user with read permission on the dataset.  | The response contains a list of DatasetImport resources. |

The list request accepts the following parameters:

| Parameter |  Value  |                   Description                    |
|-----------|---------|--------------------------------------------------|
|   limit   | integer |    The number of objects to return per page.     |
|  offset   | integer | The offset within the list of available objects. |