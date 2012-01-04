from werkzeug import parse_options_header
from flask import request


def get_blob_key(field_name, blob_key=None):
    upload_file = request.files[field_name]
    header = upload_file.headers['Content-Type']
    parsed_header = parse_options_header(header)
    blob_key = parsed_header[1]['blob-key']
    return blob_key
