# Vaults and Objects

## Overview

Vaults are similar to filesystems in that they provide a unified directory structure where folders, files, and datasets can be stored. All items in a vault (the folders, [files](https://quartzbio.github.io/quartzbio-python/querying_datasets_and_files.html#querying-files), and [datasets](https://quartzbio.github.io/quartzbio-python/creating_and_migrating_datasets.html#dataset-fields)) are collectively referred to as "objects". All vault objects can be moved, copied, renamed, tagged, and assigned [metadata](https://quartzbio.github.io/quartzbio-python/metadata_and_global_beacons.html#metadata).

Vaults also have an [advanced permission](https://quartzbio.freshdesk.com/en/support/solutions/articles/73000605485) model that provides three different levels of access: `read`, `write`, and `admin`. Vaults can be shared and permissions can be set via the EDP UI; for more information about working with vaults on the web interface as well as vault basics such as vault types, users can refer to the [Vaults via UI](https://quartzbio.freshdesk.com/en/support/solutions/articles/73000598224) documentation. 

## Creating Vaults

Users can create a vault as long as it has a unique name within their account domain. Vault and object names are `case-insensitive`. Once users create a vault, they'll be able to add folders, upload files, and create datasets. To be safe, a special method is provided to retrieve the vault by name if it already exists:

In Python:
```Python
from quartzbio import Vault

# Create a vault by name (only if it doesn't exist) in your account domain
vault_x = Vault.get_or_create_by_full_path('Vault X')

# Create a vault (fails if it already exists)
vault_x = Vault.create(name='Vault X')
```

## Retrieving Vaults

Users can retrieve any shared vault by name or the full path (e.g. domain:name). The only exception is a user's personal vault which has a special name, ~, which is also its full path. If a vault is shared with a user by someone from another organization, it must be retrieved by its full path (e.g. quartzbio:public). Users can also retrieve multiple vaults matching a given [advanced search query](https://quartzbio.github.io/quartzbio-python/vaults_and_objects.html#advanced-search) (e.g. user:username). 



```Python
from quartzbio import Vault

# Retrieve your personal vault
my_vault = Vault.get_personal_vault()

# Your personal vault also has the shortcut `~`
my_vault = Vault.get_by_full_path('~')

# Retrieve a shared vault by name
vault_x = Vault.get_by_full_path('Vault X')

# Retrieve a vault from a different domain
public_vault = Vault.get_by_full_path('quartzbio:public')

# Retrieve a vault by ID
public_vault = Vault.retrieve('19')

# Retrieve all vaults which match a given Advanced search query
specific_user_vaults = Vault.all(query='user:john')
```

## Creating Folders

Folders can only be created within a vault for which the user has write-level permission. Folder names are `case-insensitive`. If a user attempts to create a folder with a duplicate name, the vault will add an incrementing number to the name (i.e. folder, folder-1, folder-2, ...).


```Python
from quartzbio import Vault

# First, retrieve the vault
vault = Vault.get_personal_vault()

# Create the folder at the root of the vault (path is optional)
folder = vault.create_folder('new-folder', path='/')
```

## Uploading Files

Users can upload files to any vault to which they have write-level access. File names are `case-insensitive`. Uploading a file with a duplicate name (or the same name as a folder) will cause the new file's name to be auto-incremented (i.e. file, file-1, file-2, ...).

**There is no maximum upload size limit**. Users are recommended to gzip their files before uploading if they are large.



```Python
from quartzbio import Vault

# First retrieve the vault
vault = Vault.get_personal_vault()

# Upload your file into the root of the vault
vault.upload_file('local/path/data.csv', '/')
```

## Batch Uploading (Python Only)

Users can upload many files at once using the upload command built into EDP's Python module. This command is designed to be "idempotent", which means that if called more than once it will cross-check the files and upload only the local files and folders that do not yet exist in the vault. The comparison is performed by `file name` and by `file md5`.

In Terminal:

```
# Upload all the CSV files into the root of your personal vault
quartzbio upload --full-path "~/" ./*.csv

# Create the target path if not exists
quartzbio upload --full-path "~/some-non-existent-path" --create-full-path ./*.csv

# Upload CSV files, but exclude some of them by name
quartzbio upload --full-path "~/" --exclude old-csv-files/*  ./*.csv

# Run in dry run mode to see before running
quartzbio upload --full-path "~/" --exclude old-csv-files/*  ./*.csv --dry-run

# For full usage:
quartzbio upload --help
```

## Downloading Files

Users can download any existing file from a vault if they have read access to the vault:


```Python
from quartzbio import Object

# Retrieve an existing file from your personal vault
csv_file = Object.get_by_full_path('~/data.csv')

# Download it to the current directory
csv_file.download('./')
```
Users can also download more than one file in the same folder:


```Python
from quartzbio import Object, Vault

# Retrieve a vault
vault = Vault.get_personal_vault()

folder = Object.get_by_full_path("vault:/path/to/folder")
for file_ in folder.files():
     file_.download()

#Search for a particular object in the vault
files = vault.search('xyz', object_type='file')
for file in files:
    file.download()
```

The Python client can also be used to download individual files or entire folders:

```
# Download a single file
quartzbio download "~/path/to/file.txt" .

# Download a folder
quartzbio download --recursive "~/path/to/folder" local_folder

# Download a folder, but exclude hidden files and folders
quartzbio download --recursive "~/path/to/folder" local_folder --exclude "*/.*"

# Download a folder, but exclude DS_store files
quartzbio download --recursive "~/path/to/folder" local_folder --exclude "*/.DS_store"

# Download only PDF files within a folder
# --include always supersedes --exclude
quartzbio download --recursive "~/path/to/folder" local_folder --exclude "*" --include "*.pdf"

# The --delete flag will delete local files that do not match
# those found in the vault. Always use the --dry-run mode first
# with this option as it will delete files permanently.
quartzbio download --recursive "~/path/to/folder" local_folder --delete --dry-run

# For full usage:
quartzbio download --help
```

## Searching within Vaults

Users can search for files, folders, and datasets within any vault by name or other attributes. 



```Python
from quartzbio import Vault

# Retrieve a vault
vault = Vault.get_personal_vault()

# Search across files, folders, and datasets in the vault
objects = vault.search('xyz')

# Search for a particular object type: file/folder/dataset
files = vault.search('xyz AND type:file')

# List all datasets in a vault
datasets = vault.datasets()

# List all datasets in a folder
folder = next(vault.folders())
datasets = folder.datasets()

# Find all objects matching an exact filename
data_objects = vault.objects(filename='data.csv')

# Find files that contain a string
samples = vault.files(query='tumor_sample_x')

# Find files with a specific path
samples = vault.files(query='/brca/october/samples')

# Find datasets
public_vault = Vault.get_by_full_path('quartzbio:public')
clinvar = public_vault.datasets(query='clinvar')

# List all the child folders of a specific folder (subfolders)
path = 'quartzbio:public:/ClinVar'
folder = Object.get_by_full_path(path)
child_folders = [i.filename for i in folder.folders()]

# Get all the files in a folder recursively
path = 'quartzbio:Public:/ClinVar'
folder = Object.get_by_full_path(path)
files = folder.files(recursive=True)
```

## Advanced Search

Users can list all objects within a vault that match a specific pattern (i.e. find all the files within a certain folder) by providing a `case-insensitive` regular expression to the regex parameter. It is highly recommended to use `Object.search()` instead of searching by regular expression, unless it is absolutely necessary.



```Python
from quartzbio import Vault
from quartzbio import Object
# Get the public vault
public_vault = Vault.get_by_full_path('quartzbio:public')
# Find datasets using regex
clinvar_v2 = public_vault.datasets(regex='/ClinVar/2.*')

# Search for all XML files
xml_files = [i.filename for i in folder.search('*.xml.gz AND type:file')]

# List the dataset ids of every dataset that has Outcome somewhere in the path
all_outcomes = [d.id for d in Object.all(regex=".*Outcome.*", type='dataset')]

# List the filenames of all xml files within a specific path
path = 'quartzbio:Public:/MEDLINE/2.3.4-2018'
folder = Object.get_by_full_path(path)
json_files = [i.filename for i in folder.files(regex="{}.*.json.gz".format(folder.path))]

# Unix style wildcards are supported too
json_files = [i.filename for i in folder.files(glob="{}*.json.gz".format(folder.path))]
```


## Move Files Between Folders

Users can search for files in one folder using the aforementioned querying and move them to another folder.


```Python
from quartzbio import Object

# Get the full path to the current and new folder where you want to move your files
new_folder = Object.get_or_create_by_full_path("~/my/new/folder", object_type="folder")
current_folder = Object.get_or_create_by_full_path("~/my/existing/folder", object_type="folder")

# Query current folder for the specific files
files = current_folder.files(query="my_search_string")

# Change the parent id of each folder in order to move it to the new folder
for file_ in files:
    file_.parent_object_id = new_folder.id
    file_.save()
```

## Deleting Vaults and Objects

Users can delete any vault or object (file, folder, or dataset) that they have admin-level permissions on. **Deleting a vault or folder will automatically delete all its contents.**


```Python
from quartzbio import Vault

# Create an empty folder in your personal vault
vault = Vault.get_personal_vault()
folder = vault.create_folder('test-delete-folder', path='/')

# Deletion of any object requires a confirmation from the user.
# You can disable this confirmation by passing the `force=True` flag.
folder.delete()
>>> Are you sure you want to delete this object? [y/N] y
```

## API Endpoints

Methods do not accept URL parameters or request bodies unless specified. Please note that if your EDP endpoint is sponsor.edp.aws.quartz.bio, you would use sponsor.api.edp.aws.quartz.bio.

### Vaults



Request Body:

|       Property        | Value  |                                  Description                                  |
|-----------------------|--------|-------------------------------------------------------------------------------|
|         name          | string |      The name of the vault. This must be unique to your account domain.       |
|      description      | string |                   (Optional) The description of the vault.                    |
|       metadata        | object |                  (Optional) A dictionary of key/value pairs.                  |
|         tags          | object |              (Optional) A list of strings to organize the vault.              |
| default\_storage\_class | string | (Optional) The default dataset storage class to apply to any datasets created |

| Method |             HTTP Request             |        Description         |                                                                                 Authorization                                                                                 |                               Response                               |
|--------|--------------------------------------|----------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------|
|  list  | GET https://<EDP\_API\_HOST>/v2/vaults | List all available vaults. | All public vaults are included in this response. If the request is sent by an authenticated user, vaults which the user has "read" permission or higher on are also returned. | The response returns a list of vaults matching the provided filters. |
| update | PUT https://<EDP\_API\_HOST>/v2/vaults/{ID} | Update a vault. | This request requires an authorized user with "write" permission or higher on the vault. | The response contains the updated Vault resource. |

Request Body

In the request body, provide a valid Vault object (see create above).

| Method |                 HTTP Request                 |   Description   |                                 Authorization                                  |                      Response                       |
|--------|----------------------------------------------|-----------------|--------------------------------------------------------------------------------|-----------------------------------------------------|
| delete | DELETE https://<EDP\_API\_HOST>/v2/vaults/{ID} | Delete a vault. | This request requires an authorized user with "admin" permission on the vault. | The response returns "HTTP 200 OK" when successful. |
|  get   | GET https://<EDP\_API\_HOST>/v2/vaults/{ID} | Retrieve a vault's metadata. | This request requires an authorized user with "read" permission or higher on the vault. | The response contains a Vault resource. |

### Objects

| Method |              HTTP Request              |    Description    |                                                     Authorization                                                     |                    Response                     |
|--------|----------------------------------------|-------------------|-----------------------------------------------------------------------------------------------------------------------|-------------------------------------------------|
| create | POST https://<EDP\_API\_HOST>/v2/objects | Create an object. | This request requires an authorized user with "write" permission or higher to the vault that the object will go into. | The response contains a single Object resource. |

Request Body:

|     Property     |  Value  |                                                 Description                                                 |
|------------------|---------|-------------------------------------------------------------------------------------------------------------|
|    vault\_id     | integer |                              The ID of the vault that will contain the object.                              |
| parent\_object\_id | integer | The ID of the existing folder object to place the new object into. To place at "/", set this value to null. |
|     filename     | string  |       The filename of the object, not including its parent folder. This value cannot contain slashes.       |
|   object\_type   | string  |               The object\_type of the object. Must be one of "file", "folder", or "dataset".                |
|   description    |  text   |                                  (Optional) The description of the object.                                  |
|     metadata     | object  |                                 (Optional) A dictionary of key/value pairs.                                 |
|       tags       | object  |                            (Optional) A list of strings to organize the object.                             |
|  storage\_class  | string  |                                    (Optional) The dataset storage class.                                    |

| Method |             HTTP Request              |         Description         |                                               Authorization                                               |                               Response                                |
|--------|---------------------------------------|-----------------------------|-----------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------|
|  list  | GET https://<EDP\_API\_HOST>/v2/objects | List all available objects. | The response includes objects which exist inside vaults that the user has "read" permission or higher to. | The response returns a list of objects matching the provided filters. |

Parameters:

This request accepts the following parameters:

|     Property     |    Value    |                                                   Description                                                    |
|------------------|-------------|------------------------------------------------------------------------------------------------------------------|
|        id        |   integer   |                                               The ID of an object.                                               |
|    vault\_id     |   integer   |                                The ID of the vault that will contain the object.                                 |
|   vault\_name    |   string    |                                    The name of the vault containing objects.                                     |
| vault\_full\_path  |    text     |                                  The full path of the vault containing objects.                                  |
| parent\_object\_id |   integer   |   The ID of the existing folder object to place the new object into. To place at "/", set this value to null.    |
|     filename     |   string    |         The filename of the object, not including its parent folder. This value cannot contain slashes.          |
|       path       |   string    |                               The path of the object, including its parent folder.                               |
|   object\_type   |   string    |                      The type of the object. Must be one of "file", "folder", or "dataset".                      |
|      depth       |   integer   |                    The depth of the object in the Vault. Objects at the root have depth = 0.                     |
|      query       |   string    |                        A string that matches any objects whose path contains that string.                        |
|      regex       |    regex    |                A regular expression which searches objects for matching paths (case-insensitive).                |
|       glob       | text (glob) |    A glob (full path with wildcard characters) which searches objects for matching paths (case-insensitive).     |
|   ancestor\_id   |   integer   |         The ID of an ancestor object (parent folder, parent of parent folder, etc). For "/", use "null".         |
|  min\_distance   |   integer   | Used in conjunction with the ancestor\_id filter to only include objects at a minimum distance from the ancestor. |
|       tags       |   string    |                A string representing a single vault tag. Matching vaults must have this tag set.                 |
|  storage\_class  |   string    |                                    Returns datasets with this storage class.                                     |

| Method |                HTTP Request                |    Description    |                                                   Authorization                                                   |                      Response                      |
|--------|--------------------------------------------|-------------------|-------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|
| update | PUT https://<EDP\_API\_HOST>/v2/objects/{ID} | Update an object. | This request requires an authorized user with "write" permission or higher to the vault that contains the object. | The response contains the updated Object resource. |

Request Body:

In the request body, provide a valid Object body (see _create_ above).

| Method |                 HTTP Request                  |    Description    |                                                   Authorization                                                   |                      Response                       |
|--------|-----------------------------------------------|-------------------|-------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------|
| delete | DELETE https://<EDP\_API\_HOST>/v2/objects/{ID} | Delete an object. | This request requires an authorized user with "write" permission or higher to the vault that contains the object. | The response returns "HTTP 200 OK" when successful. |
|  get   | GET https://<EDP\_API\_HOST>/v2/objects/{ID} | Retrieve metadata about an object. | This request requires an authorized user with "read" permission or higher to the vault that contains the object. | The response contains an Object resource. |
| create (object copy task) | POST https://<EDP\_API\_HOST>/v2/object\_copy\_tasks | Copy an object from one vault into another. Datasets are ignored by object copy tasks. If you wish to copy a dataset, you must download it and re-import it. | This request requires an authorized user with "read" permission or higher on the source vault, and "write" permission or higher on the target vault. | The response contains a single object copy task. |

Request Body

In the request body, provide the following parameters:

|     Property     |  Value  |                                                   Description                                                    |
|------------------|---------|------------------------------------------------------------------------------------------------------------------|
| source\_vault\_id  | integer |                        The ID of the vault that contains the object which will be copied.                        |
| target\_vault\_id  | integer |                              The ID of the vault that the object will be copied to.                              |
| source\_object\_id | integer |    The ID of the object which will be copied. Must be a file or folder. Set to null to copy the entire vault.    |
| target\_object\_id | integer | The ID of the object into which the new objects will copied. Must be a folder. Set to null to copy objects to /. |

|         Method          |                  HTTP Request                   |                     Description                     |               Authorization               |                      Response                      |
|-------------------------|-------------------------------------------------|-----------------------------------------------------|-------------------------------------------|----------------------------------------------------|
| list (object copy task) | GET https://<EDP\_API\_HOST>/v2/object\_copy\_tasks | List object copy tasks created by the current user. | This request requires an authorized user. | The response contains a list of object copy tasks. |
| get (object copy task) | GET https://<EDP\_API\_HOST>/v2/object\_copy\_tasks/{ID} | Retrieve metadata about an object copy task. | This request requires that the authorized user is also the user who created the object copy task being retrieved. | The response contains an object copy task resource. |
