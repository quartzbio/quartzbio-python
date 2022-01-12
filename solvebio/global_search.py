# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .client import client
from .errors import SolveError
from .query import QueryBase
from .query import Query
from .query import Filter

import logging
logger = logging.getLogger('solvebio')


class GlobalSearch(Query):
    """
    GlobalSearch acts as a request wrapper that generates a request from Filter objects,
    and can iterate through streaming result sets.
    """

    def __init__(
            self,
            query=None,
            filters=None,
            entities=None,
            ordering=None,
            limit=float('inf'),
            page_size=QueryBase.DEFAULT_PAGE_SIZE,
            result_class=dict,
            debug=False,
            **kwargs):
        """
        Creates a new Query object.

        :Parameters:
          - `query` (optional): An optional query string.
          - `filters` (optional): Filter or List of filter objects.
          - `entities` (optional): List of entity tuples to filter on.
          - `ordering` (optional): List of fields to order the results by.
          - `limit` (optional): Maximum number of query results to return.
          - `page_size` (optional): Number of results to fetch per query page.
          - `result_class` (optional): Class of object returned by query.
          - `debug` (optional): Sends debug information to the API.
        """
        self._data_url = '/v2/search'
        self._query = query
        self._entities = entities
        self._ordering = ordering
        self._result_class = result_class
        self._debug = debug
        self._error = None
        self._is_join = False

        if filters:
            if isinstance(filters, Filter):
                filters = [filters]
        else:
            filters = []
        self._filters = filters

        # init response and cursor
        self._response = None
        # Limit defines the total number of results that will be returned
        # from a query involving 1 or more pagination requests.
        self._limit = limit
        # Page size/offset are the low level API limit and offset params.
        self._page_size = int(page_size)
        # Page offset can only be set by execute(). It is always set to the
        # current absolute offset contained in the buffer.
        self._page_offset = None
        # slice is set when the Query is being sliced.
        # In this case, __iter__() and next() will not
        # reset the page_offset to 0 before iterating.
        self._slice = None

        # parameter error checking
        if self._limit < 0:
            raise Exception('\'limit\' parameter must be >= 0')

        if not 0 < self._page_size <= self.MAX_PAGE_SIZE:
            raise Exception('\'page_size\' parameter must be in '
                            'range [1, {}]'.format(self.MAX_PAGE_SIZE))

        # Set up the SolveClient
        # (kwargs overrides pre-set, which overrides global)
        self._client = kwargs.get('client') or self._client or client

    def _clone(self, filters=None, limit=None):
        new = self.__class__(query=self._query,
                             limit=self._limit,
                             entities=self._entities,
                             ordering=self._ordering,
                             page_size=self._page_size,
                             result_class=self._result_class,
                             debug=self._debug,
                             client=self._client)
        new._filters += self._filters

        if filters:
            new._filters += filters

        if limit:
            new._limit = limit

        return new

    def __len__(self):
        """
        Returns the total number of results returned in a query. It is the
        number of items you can iterate over.

        In contrast to count(), the result does take into account any limit
        given. In SQL it is like:

              SELECT COUNT(*) FROM (
                 SELECT * FROM <table> [WHERE condition] [LIMIT number]
              )
        """
        if self._is_join:
            return len(self._buffer)

        return super(GlobalSearch, self).__len__()

    def _build_query(self, **kwargs):
        q = {}

        if self._query:
            q['query'] = self._query

        if self._filters:
            filters = self._process_filters(self._filters)
            if len(filters) > 1:
                q['filters'] = [{'and': filters}]
            else:
                q['filters'] = filters

        if self._entities is not None:
            q['entities'] = self._entities

        if self._ordering is not None:
            q['ordering'] = self._ordering

        if self._debug:
            q['debug'] = 'True'

        # Add or modify query parameters
        # (used by BatchQuery and facets)
        q.update(**kwargs)

        return q

    def execute(self, offset=0, **query):
        """
        Executes a query. Additional query parameters can be passed
        as keyword arguments.

        Returns: The request parameters and the raw query response.
        """
        _params = self._build_query(**query)
        self._page_offset = offset

        _params.update(
            offset=self._page_offset,
            limit=min(self._page_size, self._limit)
        )

        if self._is_join:
            # We do not know the exact total number of records in join because it
            # is dynamically calculated in internal expression in target_fields in
            # join() method, therefore we have to change limit in the last
            # subsequent request in order to get the given number of records from query_a
            _params['limit'] = min(self._page_size, abs(self._limit - self._page_offset))
            self._next_offset = self._page_offset + min(self._page_size, self._limit)

        logger.debug('executing query. from/limit: %6d/%d' %
                     (_params['offset'], _params['limit']))

        # If the request results in a SolveError (ie bad filter) set the error.
        try:
            self._response = self._client.post(self._data_url, _params)
        except SolveError as e:
            self._error = e
            raise

        logger.debug('query response took: %(took)d ms, total: %(total)d'
                     % self._response)
        return _params, self._response
    