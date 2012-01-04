import os

from webassets.bundle import Bundle

from app import app

try:
    from _webassets import files
except ImportError:
    files = {}


WEBASSETS_FILE = os.path.join(app.config['DIRNAME'], '_webassets.py')
WEBASSETS_TEMPLATE = "files = %(files)s"


class AppEngineBundle(Bundle):
    def update_timestamp(self, env, filename):
        filepath = env.abspath(filename)
        last_modified = os.stat(filepath).st_mtime

        files[filename] = last_modified
        content = WEBASSETS_TEMPLATE % dict(files=repr(files))
        open(WEBASSETS_FILE, 'w+').write(content)

    def make_url(self, env, filename, expire=True):
        last_modified = files.get(filename, 0)
        result = "%s?%d" % (filename, last_modified)
        return env.absurl(result)

    def _update_needed(self, env, force=False):
        if force:
            return True
        elif env.updater:
            return env.updater.needs_rebuild(self, env)
        else:
            return False

    def build(self, env=None, force=False):
        hunks = super(AppEngineBundle, self).build(env=env, force=force)
        env = self._get_env(env)
        self.update_timestamp(env, self.output)
        return hunks
