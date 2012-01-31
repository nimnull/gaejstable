from flask import url_for
from collections import defaultdict

from app import app


class Sitemap(object):
    """ Class for holding service sitemap

    Usage:
        >>>from core.sitemap import sitemap
        >>>sitemap.register('catalog.create_category',
            _('Create category'), child_of='catalog.list_categories')
    """

    def __init__(self):
        self.root = Leaf('', '')
        self.leaves = {}
        self.unattached = defaultdict(list)

    def register(self, endpoint, title, root=False, child_of=None,
            args={}):
        leaf = Leaf(endpoint, title, args)
        leaf.add_children(self.unattached.pop(endpoint, []))

        self.leaves.update({endpoint: leaf})

        if root:
            leaf.add_children(self.root.children.itervalues())
            self.root = leaf
        elif child_of is None:
            self.root.add_child(leaf)
        else:
            parent = self.leaves.get(child_of)
            if parent is None:
                self.unattached[child_of].append(leaf)
            else:
                parent.add_child(leaf)


class Leaf(object):

    def __init__(self, endpoint, title, args={}):
        self.title, self.endpoint = title, endpoint
        self.children, self.parent = {}, None
        self.args = args

    def add_child(self, child):
        child.add_parent(self)
        self.children.update({child.endpoint: child})

    def add_children(self, leaves):
        for leaf in leaves:
            self.add_child(leaf)

    def add_parent(self, parent):
        self.parent = parent

    def __unicode__(self):
        return "{} {} {}".format(self.__class__, self.title, self.endpoint)

    __repr__ = __unicode__


def breadcrumb(endpoint):

    def build(leaf, path=[]):
        path.insert(0, (leaf.title, url_for(leaf.endpoint, **leaf.args)))
        if leaf.parent is not None:
            return build(leaf.parent, path)
        else:
            return path

    leaf = sitemap.leaves.get(endpoint, None)
    path = leaf and build(leaf) or None
    return path


app.jinja_env.globals.update(breadcrumb=breadcrumb)

sitemap = Sitemap()
