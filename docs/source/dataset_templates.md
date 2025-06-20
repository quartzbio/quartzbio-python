# Dataset Templates


## Overview

Dataset templates describe how data should be transformed. A template is a collection of fields (columns) that describe the desired format of some input data. Templates are used to import files, export, query or migrate data. They allow for field normalization and transformation, and also for the addition of fields and annotations. In this article, users will learn how to view, create, update and apply templates for transforming datasets. 

## Retrieving Templates

To list all templates:

In Python:
```Python
for template in DatasetTemplate.all(template_type="dataset"):    print(template['name'], template['id'], template['account'], template['is_public'])for template in DatasetTemplate.all(template_type="dataset"):    print(template['name'], template['id'], template['account'], template['is_public'])
```


It will return all available dataset templates with their names, template id, organization, account id and status.

To retrieve a template by known ID:

In Python:
```Python
template = quartzbio.DatasetTemplate.retrieve('template_id')print(template)
```

## Template Fields

The list of fields is the most important part of a template. Each field describes a DatasetField, an object that defines properties of the field such as name, title, and data type as key-value pairs. Fields are written as dictionaries in Python and as lists in R. 

Example:

In Python:
```Python
fields = [{    "name": "reason",    "title": "Reason"    "description": "The reasons for the significance value",    "data_type": "string",    "depends_on": [        "reason_list"    ],    "expression": "', '.join(record.reason_list) if record.reason_list else None",    "ordering": 1,}{...}]
```

## Template Permissions

By default, all newly created templates are accessible by everyone at the user's organization.

If users want the template to be shown in the UI (in the modal used for transforming files), then they can add the import tag to the template.

In Python:

```Python
template = DatasetTemplate.retrieve('id of your template')template.tags = ['import']template.save()
```

If users would like to make the template private (accessible only to your user), then they can set the account\_id parameter to None.

In Python:
```Python
template = DatasetTemplate.retrieve('id of your template')template.account_id = Nonetemplate.save()
```

If users would like to make the template accessible to all users on EDP (including those outside of your organization) then they can set the is\_public parameter to True. As always, users should not share anything sensitive outside of their organization.

In Python:
```Python
template = DatasetTemplate.retrieve('id of your template')template.is_public = Truetemplate.save()
```

## Create a Template

To create a template, users should prepare the list of DatasetFields with information about data types, expressions, entities, etc.

Example of list of fields:

In Python:
```Python
fields = [{    'name': 'sample',    "depends_on": ['subject'],    "entity_type": "sample",    'description': 'Sample ID from SUBJECT',    'data_type': 'string',    'ordering': 1 ,    'expression': "record.subject"},{    'name': 'study',    'title': 'STUDY',    'description': 'Study Code',    'ordering': 2 ,    'expression': "None if value == 'UNASSIGNED' else value",    'data_type': 'string'},{    "data_type": "string",    "depends_on": [        "hgvs_c"    ],    "description": "EDP variant entity, computed from the short variant CDS change",    "expression": "entity_ids('variant', record.hgvs_c) if record.hgvs_c else None",    "is_transient": True,    "name": "variant_cdna_grch38"}]
```

The following attributes should be added:

-   `name` `-` the name of the field
    
-   `data_type` `-` the data type of the field
    
-   `entity_type` `– the` entity type (only necessary for entity querying)
    

The following attributes are optional, but responsible for much of the data transformation:

-   `expression` \- The expression that will be evaluated to populate this field's value. Put "value" to use the current value. Users can refer to the [Expressions documentation](https://quartzbio.freshdesk.com/en/support/solutions/articles/73000606023) for more information. In order to use data from another field (for comparison, splits, etc), users should make sure that they also add it to the list of fields, which will allow them to retrieve it using expression context variables: `record.name_of_field`. Users should also add the field in the depends\_on parameter.
    
-   `depends_on` \- This is a list of fields that the expression depends on. Users can add any field names here. This will ensure that those fields expressions are evaluated before its dependents. The template creation will fail if there is a circular dependency.
    
-   `is_transient` `-` A transient field is a field that is not indexed into the dataset, but calculated only while the template annotation is running. This is useful for temporary fields/variables for complex templates (default is False)
    

The following attributes are optional, and informational only, but encouraged:

-   `title` \- The field's display name, shown in the UI and in CSV/Excel exports.
    
-   `d``escription` \- Describes the contents of the field, shown in the UI.
    
-   `o``rdering` \- The order in which this column appears when retrieving data from the dataset. Order is 0-based. Default is 0
    
-   `is_hidden` \- Set to True if the field should be excluded by default from the UI.
    

After the list of the fields is prepared, other information about a template can be added:

In Python:
```Python
template = {    "name": "My Variant Template",    "version": '1.2.0',    "description": 'Import a special CSV file. Genome is assumed to be GRCh38, also has variant entity for GRCh37.',    "template_type": "dataset",    "is_public": False,    "entity_params": {        'disable': True    },    "fields": fields}
```
The template\_type should be set to "dataset".

After that, users can create the template:

In Python:
```Python
from quartzbio import DatasetTemplatetemplate = quartzbio.DatasetTemplate.create(**template)dataset = Dataset.get_or_create_by_full_path('your dataset path', fields=template.fields)# Dataset will now have the non-transient fields from the template# with desired titles/descriptions and expressionsprint(dataset.fields())# But no recordsprint(dataset.documents_count)
```

Printing the template object will show the template's ID and contents.

## Create a Dataset with a Template

Users can create a dataset and set the structure with a template.

In Python:
```Python
template = DatasetTemplate.retrieve('id of your template')dataset = Dataset.get_or_create_by_full_path('your dataset path', fields=template.fields)# Dataset will now have the non-transient fields from the template# with desired titles/descriptions and expressionsprint(dataset.fields())# But no recordsprint(dataset.documents_count)
```

Users can also create and a dataset and add the fields during file import:

In Python:
```Python
template = DatasetTemplate.retrieve('id of your template')dataset = Dataset.get_or_create_by_full_path('your dataset path')# Only field should be "id"print(dataset.fields())file_object = Object.retrieve('id of file uploaded to EDP')DatasetImport.create(    dataset_id=dataset.id,    object_id=file_object.id,    target_fields=template.fields,    commit_mode='append',)# Wait for import to finishdataset.activity(follow=True)# Should now see all the non-transient fields from the template!print(dataset.fields())
```

## Update a Template:

Template attributes such as the list of fields can be edited. For example, new fields can be added to an existing template. In this example, a new field called "phase\_numeric" is added to the template to transform roman numerals to numbers in the phase field of the dataset.

In Python:
```Python
import quartzbiofrom quartzbio import Datasetfrom quartzbio import DatasetTemplate# Retrieve a template by ID my_template = quartzbio.DatasetTemplate.retrieve('dataset_id')#Create updated list of fields as an empty listupdated_fields=[]#Get fields from my_template and add to listfor x in my_template.fields:    updated_fields.append(dict(x))# Write a new fieldphase_numeric={  "title": "phase_numeric",  "name": "phase_numeric",  "data_type": "string",  "depends_on": ["phase"],  "expression": "record.phase.replace('III', '3').replace('II', '2').replace('I', '1')"}#Add new field to updated fields listupdated_fields.append(phase_numeric)#Update template fieldsmy_template.fields=updated_fields#Save templatemy_template.save()# Test the template by applying it to a few records dataset = Dataset.get_by_full_path("vault:/my/dataset/")records=dataset.query()for record in records.annotate(my_template.fields):    print(record)#Update other attributes such as version and savemy_template.version='2.00'my_template.save()
```

## Building and Testing Templates with the Annotator

When creating new templates it it is useful to use the annotator to test and validate the fields and their expressions. The below snippet will use the annotator to process records in real time with the template fields.

In Python:
```Python
from quartzbio import Datasetfrom quartzbio import DatasetTemplate# Load fields from a templatedataset = Dataset.get_by_full_path('vault:/my/dataset/')template = DatasetTemplate.retrieve(template_id)# Retrieve and annotate records with the dataset template fieldsrecords = dataset.query()for record in records.annotate(template.fields):    print(record)# Annotate records server side (most efficient)records = dataset.query(target_fields=template.fields)# Use the Annotator classann = Annotator(fields=template.fields)records = dataset.query()for record in ann.annotate(records):    print(record)
```

## API Endpoints

Methods do not accept URL parameters or request bodies unless specified. Please note that if your EDP endpoint is sponsor.edp.aws.quartz.bio, you would use sponsor.api.edp.aws.quartz.bio.  

Dataset Templates

| Method |                   HTTP Request                    |        Description         |                             Authorization                              |                        Response                         |
|--------|---------------------------------------------------|----------------------------|------------------------------------------------------------------------|---------------------------------------------------------|
| create | POST https://<EDP\_API\_HOST>/v2/dataset\_templates | Create a dataset template. | This request requires an authorized user with appropriate permissions. | The response contains the new DatasetTemplate resource. |

Request Body:

In the request body, provide an object with the following properties:

|      Property      |  Value  |                             Description                             |
|--------------------|---------|---------------------------------------------------------------------|
|        name        | string  |                 A short name for the new template.                  |
|    description     | string  |                   A description for the template.                   |
|       fields       | objects |                   A list of valid dataset fields.                   |
|      version       | string  |        A string representing a template version (no spaces).        |
|   template\_type   | string  |          The type of template: dataset, recipe or search.           |
|     is\_public     | boolean | True if visible to anyone in a user's organization (default False). |
| annotator\_params  | object  |       (optional) Configuration parameters for the Annotator.        |
|   entity\_params   | object  |      (optional) Configuration parameters for entity detection.      |
|   reader\_params   | object  |          (optional) Configuration parameters for readers.           |
| validation\_params | object  |         (optional) Configuration parameters for validation.         |

| Method |                       HTTP Request                       |        Description         |                                  Authorization                                   |                      Response                       |
|--------|----------------------------------------------------------|----------------------------|----------------------------------------------------------------------------------|-----------------------------------------------------|
| delete | DELETE https://<EDP\_API\_HOST>/v2/dataset\_templates/{ID} | Delete a dataset template. | This request requires an authorized user with write permissions on the resource. | The response returns "HTTP 200 OK" when successful. |

|  Method  |                         HTTP Request                          |                     Description                     |                       Authorization                       |                                      Response                                      |
|----------|---------------------------------------------------------------|-----------------------------------------------------|-----------------------------------------------------------|------------------------------------------------------------------------------------|
| generate | GET https://<EDP\_API\_HOST>/v2/datasets/{DATASET\_ID}/template | Create a dataset template from an existing dataset. | This request requires an authorized user with permission. | The response contains an unsaved DatasetTemplate object for the specified dataset. |

| Method |                     HTTP Request                      |         Description          |                       Authorization                       |                     Response                      |
|--------|-------------------------------------------------------|------------------------------|-----------------------------------------------------------|---------------------------------------------------|
|  get   | GET https://<EDP\_API\_HOST>/v2/dataset\_templates/{ID} | Retrieve a dataset template. | This request requires an authorized user with permission. | The response contains a DatasetTemplate resource. |

| Method |                   HTTP Request                   |                   Description                   |                         Authorization                          |                                 Response                                  |
|--------|--------------------------------------------------|-------------------------------------------------|----------------------------------------------------------------|---------------------------------------------------------------------------|
|  list  | GET https://<EDP\_API\_HOST>/v2/dataset\_templates | Retrieve a list of available dataset templates. | This request requires an authorized user with read permission. | The response contains a list of resources visible to the requesting user. |

Parameters

This request accepts the following parameters:

| Property |  Value  |                   Description                    |
|----------|---------|--------------------------------------------------|
|  limit   | integer |    The number of objects to return per page.     |
|  offset  | integer | The offset within the list of available objects. |
