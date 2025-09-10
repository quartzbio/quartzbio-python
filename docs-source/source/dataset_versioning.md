# Dataset Versioning


## Dataset Activity

Dataset activity includes any operation that imports, transforms, exports, or copies dataset data. Users can view a dataset's activity via the API or in the EDP UI by visiting the Activity tab of a dataset.

Example: Check for any Activity

This example is a fast way to check for any activity on a dataset.

In Python:
```Python
from quartzbio import Dataset
activity = Dataset.retrieve(<DATASET ID>).activity()
if activity:
    print("Dataset has active tasks")
else:
    # run some analysis
    print("Dataset is idle")
```

Example: Wait for an Idle Dataset

Some use cases may require waiting until a dataset is idle. A dataset is idle when there are no longer any task operations that are queued, pending, or running.

This can be done synchronously using the follow parameter. This parameter continually loops through all dataset activity until the dataset is idle.

The function sleeps in between each check for activity. The default is 3 seconds and can be modified using the `sleep_seconds` parameter.

The function also limits the activity check to one task. This can be modified using the limit parameter.


```Python
from quartzbio import Dataset
Dataset.retrieve(<DATASET ID>).activity(follow=True)

# Sleep for 20 seconds in between
Dataset.retrieve(<DATASET ID>).activity(follow=True, sleep_seconds=20.0)

# Retrieve information for at most 30 active tasks
Dataset.retrieve(<DATASET ID>).activity(follow=True, limit=30)
```

## Reverting Datasets

### Overview

Dataset commits are the backbone of EDP's datastore and represent a change log of modifications to a dataset. A dataset commit represents all changes made to the target dataset by the import/migration/delete process.

All of these changes can be reverted by creating a rollback commit. All commits can be reverted. A rollback commit will restore the dataset to its state before the commit was made.

The parent commit of a rollback commit is the commit to be reverted.

### Rollbacks

A rollback commit represents a revert of a commit. The rollback commit will do different things depending on the mode of the parent commit. It may delete records, index a rollback file, or both.

A rollback file is generated for overwrite, upsert, and delete models. This file is generated right before records are committed, by querying the current state of the dataset and storing those records in a file. This file is stored with the commit object and used when creating a rollback commit. 

| **Commit Mode** |                                          **Description**                                           |
|-------------|------------------------------------------------------------------------------------------------|
|   append    |                 Reverts by deleting all records containing parent \_commit ID                  |
|   delete    |             Reverts by indexing the records deleted (stored in the rollback file)              |
|  overwrite  | Reverts by deleting all records containing parent \_commit ID. Then indexing the rollback file |
|   upsert    |                                Same as overwriting commit mode                                 |

**Checking the Ability to Rollback**

In order for a commit to be reverted, there must be a clear "commit" stack on the dataset. Commits with mode overwrite or upsert will block reverts and must be reverted first. When creating a rollback, if there are blocking commits, the endpoint will fail and return these blocking commit values.

**Example**

Imagine a simple dataset containing employee names and employee addresses. This is maintained by an annual import of employees with address changes (including new employees.) Over the course of a few years, several employees move addresses. Several employees join the company, and some leave as well.

-   Commit A (Import 2015 address file in overwrite mode)
-   Commit B (Import 2016 address file in overwrite mode)
-   Commit C (Import 2017 address file in overwrite mode)
-   Commit D (Import 2018 address file in overwrite mode)

Let's do a simple case first, where nobody actually moves addresses, and therefore only new employees are added.

If a user were to revert Commit C, then they would only remove new 2017 employees from the dataset. The 2015, 2016, and 2018 employees all remain.

Now let's assume people do move and so each year we have all sorts of address changes.

If users were to revert Commit C, then the dataset would be restored to the known state that it was in Commit B. It would only reset the 2017 addresses to 2016 addresses for people that did not also change in 2018. It would also leave any new employees added in 2018. This is an inconsistent state and not a valid snapshot of the dataset at the time Commit C was indexed. Therefore this is not allowed and attempts to rollback will fail. Commit D must be reverted first.

## Archiving Datasets

### Overview

Archiving gives users the ability to safely store the datasets that they do not use frequently, without consuming their organization's active storage space quota. When users decide that they want to use the dataset again, they can quickly and easily restore it. Depending on the [storage class](https://quartzbio.github.io/quartzbio-python/dataset_versioning_via_api.html#archiving-datasets) used, a dataset may be archived automatically.

### Permissions

A user must have write [permissions](https://quartzbio.freshdesk.com/en/support/solutions/articles/73000605647) on the vault in order to archive or restore a dataset.

### Querying

Archived datasets currently cannot be queried and will raise an error if a query is attempted. Users can check if a dataset is archived by checking its availability parameter. The value will be available, unavailable, or archived.

### Examples

Users can easily archive and restore a dataset through the UI or through the API (via Python or R).

**Archiving**

A Dataset can be archived using the `archive()` function within Python, or by changing the storage class to "Archive" within the R client.


```Python
import quartzbio as sb

# Retrieve the dataset by dataset_id
dataset = sb.Object.retrieve('dataset_id')
dataset.archive()

# Archive all datasets in a folder, recursively
folder = Object.retrieve('folder_id')
for dataset in folder.datasets(recursive=True):
    dataset.archive()
```

**Restore**

Restoring the archived dataset can be done using the `restore()` function on the archived dataset. By default, the Python client will use the "Standard" storage class. However, users may restore to any [storage class](https://quartzbio.github.io/quartzbio-python/dataset_versioning_via_api.html#archiving-datasets) that is available.


```Python
import quartzbio as sb

dataset = sb.Object.retrieve('dataset_id')
dataset.restore()
```

**Switching the Storage Class**

[Storage classes](https://quartzbio.github.io/quartzbio-python/dataset_versioning_via_api.html#archiving-datasets) can be modified from the Python/R clients as follows:


```Python
import quartzbio as sb

dataset = sb.Object.retrieve('dataset_id')

# Change the storage class to Essential
dataset.storage_class = "Essential"
dataset.save()
```

**Supporting Archived Datasets**

After the introduction of dataset archiving & restoring and of dataset [storage classes](https://quartzbio.github.io/quartzbio-python/dataset_versioning_via_api.html#archiving-datasets) (December 2020), a dataset may now be in an unavailable state. Scripts and apps must now check for this state before querying or explicitly handling query failures. Both the Dataset and the Object resources now contain the "availability" parameter which returns "available", "unavailable", "restoring" or "archived" for a dataset.

See examples below:


```Python
# Explicitly check availability
datasets = vault.datasets()
for dataset in datasets:
    if dataset.availability != 'available':
        print("Dataset {} availability is {}. Not querying.".format(dataset.id, dataset.availability))
        continue

    print(dataset.query())


# Catch errors
datasets = vault.datasets()
for dataset in datasets:
    try:
        print(dataset.query())
    except errors.SolveError:
        print("Dataset can not be queried: {}".format(e))
```

## API Endpoints

Methods do not accept URL parameters or request bodies unless specified. Please note that if your EDP endpoint is sponsor-cloud.edp.aws.quartz.bio, you would use sponsor-cloud.api.edp.aws.quartz.bio.
For correct work of the API, you need to change `<EDP_API_HOST>` to your current domain, such as my-domain.api.edp.aws.quartz.bio

### Dataset Commits

Dataset commits cannot be directly created. Commits are generated only from dataset imports.

| Method |                      HTTP Request                      |                                              Description                                              |                                  Authorization                                  |                      Response                       |
|--------|--------------------------------------------------------|-------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------|-----------------------------------------------------|
| delete | DELETE https://<EDP\_API\_HOST>/v2/dataset\_commits/{ID} | Delete a dataset commit. Deleting dataset commits is not recommended as data provenance will be lost. | This request requires an authorized user with write permissions on the dataset. | The response returns "HTTP 200 OK" when successful. |
|  get   | GET https://<EDP\_API\_HOST>/v2/dataset\_commits/{ID} | Retrieve metadata about a dataset commit. | This request requires an authorized user with permission. | The response contains a DatasetCommit resource. |
|  list  | GET https://<EDP\_API\_HOST>/v2/datasets/{DATASET\_ID}/commits | Retrieve a list of dataset commits associated with a dataset. | This request requires an authorized user with read permission on the dataset. | The response contains a list of DatasetCommit resources. |
| revert status | GET https://<EDP\_API\_HOST>/v2/dataset\_commits/{ID}/rollback | Returns whether or not a commit can be reverted and returns a reason why along with any commits that are blocking. | This request requires an authorized user with write permissions on the dataset. | Returns a boolean _is\_blocked_ and a detail string explaining why. If there are blocking commits _blocking\_commits_ will contain a list of DatasetCommit resources. |
| revert | POST https://<EDP\_API\_HOST>/v2/dataset\_commits/{ID}/rollback | Revert a completed commit by creating a rollback. | This request requires an authorized user with write permission on the dataset. | If a rollback cannot be created, the status code will be 400 Bad Request. Otherwise, the response will contain a DatasetCommit resource, representing the rollback commit. |
| cancel | PUT https://<EDP\_API\_HOST>/v2/datasets\_commits/{ID}/cancel | Cancel a dataset commit. | This request requires an authorized user with read permission on the dataset. | The response will contain a DatasetCommit resource with the status canceled. |

Request Body:

In the request body, provide a valid DatasetCommit object with status = canceled.

### Dataset Restore Tasks

| Method |                             HTTP Request                              |                   Description                   |                                    Authorization                                    |                       Response                       |
|--------|-----------------------------------------------------------------------|-------------------------------------------------|-------------------------------------------------------------------------------------|------------------------------------------------------|
|  get   | GET https://<EDP\_API\_HOST>/v2/dataset\_restore\_tasks/{RESTORE\_TASK\_ID} | Retrieve metadata about a dataset restore task. | This request requires an authorized user with read permission for the restore task. | The response contains a DatasetRestoreTask resource. |
|  list  | GET https://<EDP\_API\_HOST>/v2/dataset\_restore\_tasks | Retrieve a list of available dataset restore tasks. | This request requires an authorized user with read permission for the restore tasks. | The response contains a list of DatasetRestoreTask resources. |

### Dataset Snapshot Tasks

Dataset snapshot tasks can not be created directly. They are created when a dataset's storage class is set to Archive.

| Method |                              HTTP Request                               |                   Description                    |                                    Authorization                                     |                       Response                        |
|--------|-------------------------------------------------------------------------|--------------------------------------------------|--------------------------------------------------------------------------------------|-------------------------------------------------------|
|  get   | GET https://<EDP\_API\_HOST>/v2/dataset\_snapshot\_tasks/{SNAPSHOT\_TASK\_ID} | Retrieve metadata about a dataset snapshot task. | This request requires an authorized user with read permission for the snapshot task. | The response contains a DatasetSnapshotTask resource. |
|  list  | GET https://<EDP\_API\_HOST>/v2/dataset\_snapshot\_tasks | Retrieve a list of available dataset snapshot tasks. | This request requires an authorized user with read permission for the snapshot tasks. | The response contains a list of DatasetSnapshotTask resources. |
