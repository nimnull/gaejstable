from google.appengine.ext import blobstore
from google.appengine.api.blobstore import BlobNotFoundError

from flask import abort, redirect, url_for, Response
from flaskext.babel import gettext as _

from auth.decorators import login_required


from . import core
from .sitemap import sitemap


@core.route('/')
@login_required
def index():
    return redirect(url_for('catalog.filtered_records'))


sitemap.register('core.index', _('Main'), root=True)


@core.route('/serve/<key>')
def serve(key):
    """ Endpoint for serving files

    Serves files from the blobstore by the given blob-key string

    Args:
        key: string value of BlobKey

    Returns:
        flask.Response object with the mimetype given by the BlobInfo
        entity

    Raises:
        NotFoundException in case of requested blog is nonexistent
    """

    try:
        blob_info = blobstore.get(key)
    except BlobNotFoundError:
        abort(404)

    response = Response(mimetype=blob_info.content_type, headers={
        'content-length': blob_info.size,
        'Content-Disposition': "attachment; filename=%s" % blob_info.filename
        })
    response.stream.writelines(_reader(blob_info))
    return response


def _reader(blob_info, chunk_size=1024):
    """ Helper generator for reading chunked content from the blobstore
    """
    position = 0
    while position < blob_info.size:
        yield blobstore.fetch_data(blob_info, position,
                position + chunk_size)
        position += chunk_size + 1
