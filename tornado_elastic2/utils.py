from elasticapm.conf import constants
from elasticapm.utils import compat, get_url_dict
from elasticapm.utils.wsgi import get_environ, get_headers


def get_data_from_request(request, capture_body=False, capture_headers=True):
    url = '{}://{}{}'.format(request.protocol, request.host, request.uri)
    data = {
        "method": request.method,
        "socket": {
            "remote_address": request.remote_ip,
            "encrypted": request.protocol == 'https'
        },
        "cookies": dict(**request.cookies),
        "url": get_url_dict(url)
    }

    if capture_headers:
        data["headers"]  = dict(**request.headers)
        data["headers"].pop("Cookie", None)

    if capture_body:
        if request.method in constants.HTTP_WITH_BODY:
            body = None
            content_type = request.headers.get("content-type")
            content_type_lower = content_type.lower() if content_type else None
            if content_type_lower == "application/x-www-form-urlencoded":
                body = compat.multidict_to_dict(request.form)
            elif content_type_lower and content_type_lower.startswith("multipart/form-data"):
                body = compat.multidict_to_dict(request.form)
                if request.files:
                    body["_files"] = {
                        field: val[0].filename if len(val) == 1 else [f.filename for f in val]
                        for field, val in compat.iterlists(request.files)
                    }
            else:
                body = request.body

            if body:
                data["body"] = body

    return data


def get_data_from_response(response, capture_headers=True):
    data = {"status_code": response.get_status()}
    if capture_headers and response._headers:
        data["headers"] = response._headers._dict
    return data
