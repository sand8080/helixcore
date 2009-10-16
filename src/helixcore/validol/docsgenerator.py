from validol import AnyOf, Text
from helixcore.validol.validol import Optional, Positive
import os

def block_brace(s):
    return '<div class="brace">%s</div>' % s

def inline_brace(s):
    return '<span class="brace">%s</span>' % s

def string(s):
    return '<span class="string">"%s"</span>' % s

def atomic_type(s):
    return '<span class="variable">%s</span>' % s

def block(s):
    return '<div class="block">%s</div>' % s

def line(s):
    return '<div>%s</div>' % (s)

def optional_line(s):
    return '<div class="optional">%s %s</div>' % (s, line_comment('optional'))

def block_comment(s):
    return '<div class="comment">// %s</div>' % s

def line_comment(s):
    return '<span class="comment">// %s</span>' % s

def propname(s):
    return '<span class="property">%s</span>' % s

def indent(*args):
    return '<div class="indent">%s</div>' % ''.join(args)

def format_hash(data):
    lines = []
    is_last = lambda i, last_i=len(data) - 1: i == last_i
    for i, (key, value) in enumerate(data.items()):
#        if comment:
#            lines.append(block_comment(comment))
        if isinstance(key, Optional):
            lines.append(optional_line('%s %s%s' % (propname(safe(key.data) + ':'), format(value), '' if is_last(i) else ',')))
        else:
            lines.append(line('%s %s%s' % (propname(safe(key) + ':'), format(value), '' if is_last(i) else ',')))
    return block_brace('{') + indent(''.join(lines) or block_comment('empty')) + block_brace('}')

def format(data):
    if isinstance(data, basestring):
        return string(data)
    if isinstance(data, AnyOf):
        return OR(data.validators)
    if isinstance(data, type):
        if data == bool:
            return atomic_type(safe('( true | false )'))
        else:
            return atomic_type(safe('!!!! type %s !!!' % data))
    if isinstance(data, list):
        assert len(data) == 1
        return atomic_type('[%(t)s]' % {'t': format(data[0])})
    if isinstance(data, Text):
        return atomic_type(safe('string'))
    if isinstance(data, Positive):
        return atomic_type(safe('positive integer'))
    if isinstance(data, dict):
        #print 'data', data
        return format_hash(data)
    return block_comment('%s not supported' % safe(type(data)))
    #raise NotImplementedError('%s not supported' % type(data))

def safe(s):
    return str(s).replace('<', '&lt;').replace('>', '&gt;')

def OR(lst):
    if len(lst) < 2:
        return block(format(lst[0]))
    else:
        return (
            '<table class="branching">'
                '<tr valign="top">'
                    '%s'
                '</tr>'
            '</table>') % (
                '<td class="branch_splitter"></td>'.join(
                    '<td class="branch">%s</td>' % format(item) for item in lst
                )
            )

root = os.path.dirname(__file__)
def get_css():
    return open(os.path.join(root, 'json-docs.css')).read()

# Useful for documentation generation
class DocItem(object):
    def __init__(self, name, scheme, description='Not described at yet.'):
        self.name = name
        self.scheme = scheme
        self.description = description

        self.io_type = ''
        self.cleaned_name = self.name

        if '_' in self.name:
            cleaned_name, io_type = self.name.rsplit('_', 1)
            if io_type in ('request', 'response'):
                self.io_type = io_type
                self.cleaned_name = cleaned_name

def generate_by_protocol(protocol, title='Untitled'):
    requests =  [c for c in protocol if c.io_type == 'request']
    responses = [c for c in protocol if c.io_type == 'response']
    other =     [c for c in protocol if not c.io_type]

    items = []
    for req, resp in zip(requests, responses):
        assert req.cleaned_name == resp.cleaned_name
        items.append('<div class="item">'
            '<h2>%s</h2>'
            '<p>%s</p>'
            '<h3>request</h3>'
            '<div class="io-input">'
                '%s'
            '</div>'
            '<h3>response</h3>'
            '<div class="io-output">'
                '%s'
            '</div>'
        '</div>' % (
            req.cleaned_name,
            req.description,
            format(req.scheme),
            format(resp.scheme),
        ))


    for c in other:
        items.append('<div class="item">'
            '<h2>%s</h2>'
            '<p>%s</p>'
            '%s'
        '</div>' % (
            c.name,
            c.description,
            format(c.scheme)
        ))

    core = ''.join(items)

    return (
        '<html>'
            '<head>'
                '<title>'
                    '%(title)s'
                '</title>'
                '<style>'
                    '%(css)s'
                '</style>'
            '</head>'
        '<body>'
            '<div class="json-docs">'
                '<h1>%(title)s</h1>'
                '%(core)s'
            '</div>'
        '</body>'
        '</html>' % {
            'title': title,
            'css': get_css(),
            'core': core,
        }
    )

