"""
Minimal library for interacting with REDCap's web API.
"""
import logging
import re
import requests
from enum import Enum
from functools import lru_cache, wraps
from operator import itemgetter
from typing import Any, Dict, List


LOG = logging.getLogger(__name__)


class Project:
    """
    Interact with a REDCap project via the REDCap web API.

    The constructor requires an *api_url* and *api_token* which must point to
    REDCap's web API endpoint.  The third required parameter *project_id* must
    match the project id returned by the API.  This is a sanity check that the
    API token is for the intended project, since tokens are project-specific.
    """
    api_url: str
    api_token: str
    base_url: str
    _details: dict
    _instruments: List[str] = None

    def __init__(self, api_url: str, api_token: str, project_id: int) -> None:
        self.api_url = api_url
        self.api_token = api_token

        # Assuming that the base url for a REDCap instance is just removing the
        # trailing 'api' from the API URL
        self.base_url = re.sub(r'api/?$', '', api_url)

        # Sanity check project details
        self._details = self._fetch("project")

        assert self.id == project_id, \
            f"REDCap API token provided for project {project_id} is actually for project {self.id} ({self.title!r})!"


    @property
    def id(self) -> int:
        """Numeric ID of this project."""
        return self._details["project_id"]


    @property
    def title(self) -> str:
        """Name of this project."""
        return self._details["project_title"]


    @property
    def instruments(self) -> List[str]:
        """
        Names of all instruments in this REDCap project.
        """
        if not self._instruments:
            nameof = itemgetter("instrument_name")
            self._instruments = list(map(nameof, self._fetch("instrument")))

        return self._instruments


    def record(self, record_id: int) -> List[dict]:
        """
        Fetch the REDCap record *record_id* with all its instruments.

        Note that in longitudinal projects with events or classic projects with
        repeating instruments, this may return more than one result.  The
        results will be share the same record id but be differentiated by the
        fields ``redcap_event_name``, ``redcap_repeat_instrument``, and
        ``redcap_repeat_instance``.
        """
        return self.records(ids = [record_id])


    def records(self, since_date: str = None, ids: List[int] = None, raw: bool = False) -> List[dict]:
        """
        Fetch records for this REDCap project.

        Values are returned as string labels not numeric ("raw") codes.

        The optional *since_date* parameter can be used to limit records to
        those created/modified after the given timestamp, which must be
        formatted as ``YYYY-MM-DD HH:MM:SS`` in the REDCap server's configured
        timezone.

        The optional *ids* parameter can be used to limit results to the given
        record ids.

        The optional *raw* parameter controls if numeric values are returned
        for multiple choice fields.  When false (the default), string labels
        are returned.
        """
        parameters = {
            'type': 'flat',
            'rawOrLabel': 'raw' if raw else 'label',
            'exportCheckboxLabel': 'true',
        }

        if since_date:
            parameters['dateRangeBegin'] = since_date

        if ids is not None:
            parameters['records'] = ",".join(map(str, ids))

        return self._fetch("record", parameters)


    def _fetch(self, content: str, parameters: Dict[str, str] = {}) -> Any:
        """
        Fetch REDCap *content* with a POST request to the REDCap API.

        Consult REDCap API documentation for required and optional parameters
        to include in API request.
        """
        LOG.debug(f"Fetching content={content} from REDCap with params {parameters}")

        headers = {
            'Content-type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }

        data = {
            **parameters,
            'content': content,
            'token': self.api_token,
            'format': 'json',
        }

        response = requests.post(self.api_url, data=data, headers=headers)
        response.raise_for_status()

        return response.json()


@lru_cache()
def CachedProject(api_url: str, api_token: str, project_id: int) -> Project:
    """
    Memoized constructor for a :class:`Project`.

    Useful when loading projects dynamically, e.g. from REDCap DET
    notifications, to avoid the initial fetch of project details every time.
    """
    return Project(api_url, api_token, project_id)


class InstrumentStatus(Enum):
    """
    Numeric and string codes used by REDCap for instrument status.
    """
    Incomplete = 0
    Unverified = 1
    Complete = 2


def is_complete(instrument: str, data: dict) -> bool:
    """
    Test if the named *instrument* is marked complete in the given *data*.

    The *data* may be a DET notification or a record.

    >>> is_complete("test", {"test_complete": "Complete"})
    True
    >>> is_complete("test", {"test_complete": 2})
    True
    >>> is_complete("test", {"test_complete": "2"})
    True
    >>> is_complete("test", {"test_complete": "Incomplete"})
    False
    >>> is_complete("test", {})
    False
    """
    return data.get(f"{instrument}_complete") in {
        InstrumentStatus.Complete.name,
        InstrumentStatus.Complete.value,
        str(InstrumentStatus.Complete.value)
    }