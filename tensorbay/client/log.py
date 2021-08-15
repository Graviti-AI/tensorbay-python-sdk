# !/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Logging utility functions.

:meth:`Dump_request_and_response <dump_request_and_response>` dumps http request and response.

"""

import json
from typing import MutableMapping

from requests.models import PreparedRequest, Response
from requests_toolbelt.multipart.encoder import FileWrapper, MultipartEncoder

REQUEST_TEMPLATE = """
===================================================================
########################## HTTP Request ###########################
"url": {}
"method": {}
"headers": {}
"body": {}
"""

RESPONSE_TEMPLATE = """
########################## HTTP Response ##########################
"url": {}
"status_code": {}
"reason": {}
"headers": {}
"content": {}
===================================================================
"""


UPLOAD_DATASET_RESUME_TEMPLATE = """
*****************************************************************************
 This upload action was interrupted.
 The draft number is %d.
 To resume this upload, please pass the draft number to the upload function:

     gas.upload_dataset(dataset, draft_number=%d, skip_uploaded_files=True)

*****************************************************************************
"""

UPLOAD_SEGMENT_RESUME_TEMPLATE = """
*****************************************************************************
 This upload action was interrupted.
 The draft number is %d.
 To resume this upload, please checkout to the previous dataset draft first:

     dataset_client.checkout(draft_number=%d)
     dataset_client.upload_segment(segment, skip_uploaded_files=True)

*****************************************************************************
"""


class RequestLogging:
    """This class used to lazy load request to logging.

    Arguments:
        request: The request of the request.

    """

    def __init__(self, request: PreparedRequest) -> None:
        self._request = request

    def __str__(self) -> str:
        return _dump_request(self._request)


class ResponseLogging:
    """This class used to lazy load response to logging.

    Arguments:
        response: The response of the request.

    """

    def __init__(self, response: Response) -> None:
        self._response = response

    def __str__(self) -> str:
        return dump_request_and_response(self._response)


def dump_request_and_response(response: Response) -> str:
    r"""Dumps http request and response.

    Arguments:
        response: Http response and response.

    Returns:
        Http request and response for logging, sample::

            ===================================================================
            ########################## HTTP Request ###########################
            "url": https://gas.graviti.cn/gatewayv2/content-store/putObject
            "method": POST
            "headers": {
              "User-Agent": "python-requests/2.23.0",
              "Accept-Encoding": "gzip, deflate",
              "Accept": "*/*",
              "Connection": "keep-alive",
              "X-Token": "c3b1808b21024eb38f066809431e5bb9",
              "Content-Type": "multipart/form-data; boundary=5adff1fc0524465593d6a9ad68aad7f9",
              "Content-Length": "330001"
            }
            "body":
            --5adff1fc0524465593d6a9ad68aad7f9
            b'Content-Disposition: form-data; name="contentSetId"\r\n\r\n'
            b'e6110ff1-9e7c-4c98-aaf9-5e35522969b9'

            --5adff1fc0524465593d6a9ad68aad7f9
            b'Content-Disposition: form-data; name="filePath"\r\n\r\n'
            b'4.jpg'

            --5adff1fc0524465593d6a9ad68aad7f9
            b'Content-Disposition: form-data; name="fileData"; filename="4.jpg"\r\n\r\n'
            [329633 bytes of object data]

            --5adff1fc0524465593d6a9ad68aad7f9--

            ########################## HTTP Response ###########
            "url": https://gas.graviti.cn/gatewayv2/content-stor
            "status_code": 200
            "reason": OK
            "headers": {
              "Date": "Sat, 23 May 2020 13:05:09 GMT",
              "Content-Type": "application/json;charset=utf-8",
              "Content-Length": "69",
              "Connection": "keep-alive",
              "Access-Control-Allow-Origin": "*",
              "X-Kong-Upstream-Latency": "180",
              "X-Kong-Proxy-Latency": "112",
              "Via": "kong/2.0.4"
            }
            "content": {
              "success": true,
              "code": "DATACENTER-0",
              "message": "success",
              "data": {}
            }
            ====================================================

    """
    return _dump_request(response.request) + _dump_response(response)


def _dump_request(request: PreparedRequest) -> str:
    """Dump http request.

    Arguments:
        request: Http request.

    Returns:
        String of http request for logging.

    """
    headers = _dump_headers(request.headers)
    body = "N/A"
    if "Content-Type" in request.headers:
        if request.headers["Content-Type"].startswith("multipart/form-data"):
            body = _dump_multipart_encoder(request.body)
        elif isinstance(request.body, bytes):
            body = request.body.decode("unicode_escape")

    return REQUEST_TEMPLATE.format(request.url, request.method, headers, body)


def _dump_response(response: Response) -> str:
    """Dump http response.

    Arguments:
        response: Http response.

    Returns:
        String of http response for logging.

    """
    headers = _dump_headers(response.headers)
    content = "N/A"

    if "Content-Type" in response.headers:
        content_type = response.headers["Content-Type"]
        if content_type.startswith("application/json"):
            content = json.dumps(response.json(), indent=2)
        elif content_type.startswith("text"):
            content = response.text
        elif len(response.content) > 512:
            content = f"[{len(response.content)} bytes of object data]"
        else:
            content = str(response.content)

    return RESPONSE_TEMPLATE.format(
        response.url, response.status_code, response.reason, headers, content
    )


def _dump_multipart_encoder(body: MultipartEncoder) -> str:
    """Dump MultipartEncoder multipart/form-data Content-Type post_data.

    Arguments:
        body: MultipartEncoder multipart/formdata post data.

    Returns:
        String of multipart/form-data post data for logging.

    """
    lines = []
    boundary = body.boundary
    for part in body.parts:
        lines.append("\n" + boundary)
        lines.append(str(part.headers))
        body = part.body
        if isinstance(body, FileWrapper):
            if body.fd.closed:
                lines.append("[file closed]")
            else:
                lines.append(f"[{body.fd.tell()} bytes of object data]")
        else:
            lines.append(str(body.getvalue()))

    lines.append("\n" + boundary + "--")

    return "\n".join(lines)


def _dump_headers(headers: MutableMapping[str, str]) -> str:
    """Dump http headers as json format string for logging.

    Arguments:
        headers: Headers of http request or response.

    Returns:
        Json format string of headers content.

    """
    return json.dumps(dict(headers), indent=2)
