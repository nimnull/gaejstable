import sys
import os
import logging
import pytest


def pytest_addoption(parser):
    group = parser.getgroup("gae", "google app engine plugin")
    group.addoption('--with-gae', action='store_true', dest='use_gae',
                    default=False, help='Use pytest_gae plugin')
    group.addoption('--gae-path', action='store', dest='gae_path',
                    metavar='PATH', default='./google_appengine/',
                    help="Google App Engine's root PATH")
    group.addoption('--gae-project-path', action='store', dest='gae_prj_path',
                    metavar='PATH', default='./',
                    help="Your project's source code's PATH")


def pytest_configure(config):
    if not config.option.use_gae:
        return

    _add_gae_to_syspath(config.option.gae_path)
    _add_project_to_syspath(config.option.gae_prj_path)

    _validate_gae_path(config.option.gae_path)
    _validate_project_path(config.option.gae_prj_path)



def pytest_runtest_setup(item):
    if not item.config.option.use_gae:
        return

    gae_path = item.config.option.gae_path
    project_path = item.config.option.gae_prj_path

    from google.appengine.tools import dev_appserver
    from google.appengine.tools.dev_appserver_main import DEFAULT_ARGS

    config = DEFAULT_ARGS.copy()
    config.update({'template_dir': os.path.join(gae_path, 'templates'),
                   'blobstore_path': '/tmp/dev_appserver.test_blobstore',
                   'root_path': project_path,
                   'history_path': '/tmp/dev_appserver.datastore.test_history',
                   'datastore_path': '/tmp/dev_appserver.test_datastore',
                   'matcher_path': '/tmp/dev_appserver.test_matcher',
                   'clear_datastore': True})

    app_cfg, _junk = dev_appserver.LoadAppConfig(project_path, {})
    dev_appserver.SetupStubs(app_cfg.application, **config)


def pytest_runtest_teardown(item):
    # There is some problems with GAE and
    # py.test miscomunication that causes
    # closed stream handler to be flushed.
    #
    # Wich of course causes Exception and
    # some nasty errors at the end of testing.
    #
    # This nasty hack prevents that error to be
    # displayed.
    for h in logging.getLogger().handlers:
        if isinstance(h, logging.StreamHandler):
            _attach_save_flush(h)


def _add_gae_to_syspath(path):
    """ Adds Google App Engine and libs that comes with GAE to sys.path

    It is hardcoded and Google may change its internal structure anytime.
    So, it is not the safetest method to do it
    """

    sys.path.append(path)
    sys.path.append(os.path.join(path, 'google'))
    sys.path.append(os.path.join(path, 'lib/antlr3'))
    sys.path.append(os.path.join(path, 'lib/django'))
    sys.path.append(os.path.join(path, 'lib/fancy_urllib'))
    sys.path.append(os.path.join(path, 'lib/graphy'))
    sys.path.append(os.path.join(path, 'lib/ipaddr'))
    sys.path.append(os.path.join(path, 'lib/simplejson'))
    sys.path.append(os.path.join(path, 'lib/webob'))
    sys.path.append(os.path.join(path, 'lib/yaml/lib'))


def _add_project_to_syspath(path):
    sys.path.append(path)


def _validate_gae_path(path):
    try:
        import google.appengine
    except ImportError:
        raise pytest.UsageError("google.appengine lib can not be imported. "
                                "Try to use --gae-path option. "
                                "Current path: <%s> " % path)

def _validate_project_path(path):
    # Google App Engine projects must contain app.yaml at their roots.
    # So, this code just checks if app.yaml exists
    if not os.path.exists(os.path.join(path, 'app.yaml')):
        raise pytest.UsageError("Your AppEngine's project can not "
                                "be found. Try to use --gae-project-path "
                                "option. Current path: <%s>" % path)


def _attach_save_flush(handler):
    def save_flush():
        if not handler.stream.closed:
            handler.stream.flush()

    handler.flush = save_flush
