# Metadata and Global Beacons


## Overview

Users with Write or Admin permissions on vault objects (files, folders, and datasets) have the ability to add tags or metadata to those objects to facilitate data discovery and accessibility. Users with Write or Admin permissions on datasets can also add special labels called entities to fields that contain information such as genes, variants, and samples. To enable users to search for datasets based on the entities they contain, Admins can enable Global Beacons indexing for datasets. For more information about Search tools and data discovery on the EDP, users can refer to the [Data Discovery via API](https://quartzbio.freshdesk.com/en/support/solutions/articles/73000598413) documentation.

Tags

Tags are case-insensitive lists of strings. Tags can be used to filter and search for objects.

In Python:
```Python
from quartzbio import Vault

# Upload a file or retrieve one
vault = Vault.get_personal_vault()
csv_file = vault.upload_file('data.csv', '/')

# Add some tags to the object
csv_file.tags = ['tag1', 'tag2']
csv_file.save()

# There are also shortcuts to add and remove tags
csv_file.tag('tag3')
csv_file.untag('tag1')
```

## Metadata

Metadata is represented by key/value pairs. While nested value pairs are allowed, users are recommended to use a flat metadata structure.

In Python:
```Python
from quartzbio import Vault

# Upload a file or retrieve one
vault = Vault.get_personal_vault()
csv_file = vault.upload_file('data.csv', '/')

# Add metadata to the object
csv_file.metadata = {'file_type': 'CSV', 'project': 'My Project'}
csv_file.save()
```

Any metadata values that contain URLs will be converted to links on the EDP web interface.

## Entities

Entities are special labels for dataset fields that contain specific content, such as genes, variants, vault objects, samples, and more. Entities allow for cross-dataset data harmonization, easy filtering, Global Beacons, and other entity-specific functions. For more information about Entities and Global Beacon Search, users can refer to the [Global Beacon Search](https://quartzbio.freshdesk.com/en/support/solutions/articles/73000603092) documentation.

In the Python client library, entities can be added, removed, or changed for any field on any dataset where the user has to Write access using the fields method:

```Python
from quartzbio import Dataset
from quartzbio import DatasetField

#Get dataset
dataset=Dataset.get_by_full_path('~/my_dataset')

#Get dataset field to modify
field=dataset.fields("field_name")

#View field entity type
field.entity_type

#Output:
'gene'

#Change entity type
field.entity_type='variant'
field.save()

#Remove entity type
field.entity_type=None
field.save()
```

Entities can also be added, removed, or switched using the web interface for any dataset to which the user has write access. On the dataset view, any field with an orange label next to the field type is an entity field. Entities can be changed by clicking on the pencil icon. For more information on setting entities via the UI, users can refer to the [Modifying Datasets](https://quartzbio.freshdesk.com/en/support/solutions/articles/73000612157) documentation.

## Global Beacons

Global Beacons are specialized search endpoints that enable anyone in a user's organization to find datasets based on the entities they contain (i.e. variants, genes). Both the datasets in the public and in the private vaults can be indexed. Depending on the dataset size, indexing time may vary.

Once the dataset has been indexed, users will be able to perform Global Beacon Search and find this dataset.

The EDP Python and R clients provide the functionality to work with Global Beacons. Users with Admin permissions for a dataset can check the status of the Global Beacon on the dataset as well as enable or disable Global Beacons. 

When working with Global Beacons via API, the output will display the status attribute, which is either indexing, completed, or destroying, as well as the progress\_percent attribute which describes the percentage of the task completed. While indexing is still in progress, users won't be able to perform Global Beacon Search for that dataset. A dataset is available for Global Beacon Search when the progress\_percent is 100 and the status is completed.

In Python:
```Python
 Getting the dataset
dataset = Dataset.get_by_full_path('~/beacon-test-dataset')

# Enabling Global Beacon on dataset
dataset.enable_global_beacon()

# Example Output:
{'id': 125,
'datastore_id': 6,
'dataset_id': 1658666726768179211,
'status': 'indexing',
'progress_percent': 0,
'is_deleted': False}

# Getting the status of global beacon on the dataset
dataset.get_global_beacon_status()

# Example Output:
{'id': 125,
'datastore_id': 6,
'dataset_id': 1658666726768179211,
'status': 'completed',
'progress_percent': 100,
'is_deleted': False}

# Disabling Global Beacon on dataset
dataset.disable_global_beacon()

# Example Output:
{'id': 125,
'datastore_id': 6,
'dataset_id': 1658666726768179211,
'status': 'destroying',
'progress_percent': 0,
'is_deleted': False}
```

Users should note that upsert, overwrite, and delete commits are not yet supported by Global Beacon Search. If an indexed dataset has upsert, overwrite, or delete commits, Global Beacon search results may be inaccurate. To ensure accurate search results, users should copy the dataset (via the [UI](https://quartzbio.freshdesk.com/en/support/solutions/articles/73000614046) or [API](https://quartzbio.freshdesk.com/en/support/solutions/articles/73000613900)) and enable Global Beacons on the new one instead. For more information about commits, users can refer to the [Importing Data](https://quartzbio.freshdesk.com/en/support/solutions/articles/73000613899) documentation.
