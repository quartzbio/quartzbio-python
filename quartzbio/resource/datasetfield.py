"""QuartzBio DatasetField API Resource"""

from .quartzbio_object import convert_to_quartzbio_object
from .apiresource import CreateableAPIResource
from .apiresource import ListableAPIResource
from .apiresource import UpdateableAPIResource
from .apiresource import DeletableAPIResource


class DatasetField(
    CreateableAPIResource,
    ListableAPIResource,
    DeletableAPIResource,
    UpdateableAPIResource,
):
    """
    Each QuartzBio dataset has a different set of fields, some of
    which can be used as filters. Dataset field resources provide
    users with documentation about each field.
    """

    RESOURCE_VERSION = 2

    def facets(self, **params):
        response = self._client.get(self.facets_url, params)
        return convert_to_quartzbio_object(response, client=self._client)

    def help(self):
        return self.facets()
