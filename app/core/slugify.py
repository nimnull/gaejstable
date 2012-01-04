import re
import random
from unidecode import unidecode


word_re = re.compile(r'[^a-z0-9]+', re.UNICODE)
uppercase_re = re.compile(r'([A-Z]+)', re.UNICODE)


def slugify(text, delim=u'-'):
    text = unidecode(text)
    text = uppercase_re.sub(r'%s\1' % delim, text)
    text = text.lower()
    text = word_re.sub(delim, text)
    text = text.strip(delim)
    return text


def get_unique_slug(cls, value, Unique):
    def is_unique(slug):
        return Unique.create('%s.slug.%s' % (cls.__name__, slug))

    for i in xrange(10):
        if i:
            slug = slugify('%s %d' % (value, i))
        else:
            slug = slugify(value)
        if is_unique(slug):
            return slug

    for i in xrange(10):
        i = random.randint(11, 999999)
        slug = slugify('%s %d' % (value, i))
        if is_unique(slug):
            return slug

    raise Exception('Can not create unique slug for class %r and %r' %
                    (cls, value))
