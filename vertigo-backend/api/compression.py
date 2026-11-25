import gzip

from flask import request

MIN_BYTES = 1024


def gzip_json(response):
    if (response.status_code != 200 or response.mimetype != 'application/json'
            or response.direct_passthrough or response.content_encoding
            or request.accept_encodings.quality('gzip') <= 0):
        return response
    data = response.get_data()
    if len(data) < MIN_BYTES:
        return response
    response.set_data(gzip.compress(data, 6))
    response.content_encoding = 'gzip'
    response.vary.add('Accept-Encoding')
    return response
