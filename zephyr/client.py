from typing import Any, Callable, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

DEFAULT_BASE_URL = "https://api.zephyrscale.smartbear.com/v2"
RETRY_STATUS_CODES = {408, 429, 500, 502, 503, 504}


class Client:
    """A client for the Zephyr system."""

    def __init__(self,
                 bearer_token: str,
                 base_url: str = DEFAULT_BASE_URL):
        self.bearer_token = bearer_token
        self.base_url = base_url
        self.session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=RETRY_STATUS_CODES)
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def _request(self, method: str,
                 url: str,
                 params: Optional[dict] = None,
                 data: Optional[dict] = None,
                 headers: Optional[dict] = None,
                 extract_body: Optional[Callable] = None,
                 requests_kwargs: Optional[dict] = None
                 ) -> Any:
        """Sends an HTTP request using the given method and URL.

        :param method: HTTP method name (e.g., 'GET', 'POST', etc.)
        :param url: URL to send the request to
        :param params: Optional dictionary of query string parameters to include in the request URL
        :param data: Optional dictionary of data to include in the request body
        :param headers: Optional dictionary of headers to include in the request
        :param extract_body: Optional function that extracts the response body from the response object
        :param requests_kwargs: Optional dictionary of additional keyword arguments to pass to the requests library"""

        response = self.session.request(method, url, params=params, data=data, headers=headers, **(requests_kwargs or {}))

        # Raise an exception for any non-successful status codes
        response.raise_for_status()
        if extract_body:
            result = extract_body(response)
        else:
            result = response.json()
        return result
