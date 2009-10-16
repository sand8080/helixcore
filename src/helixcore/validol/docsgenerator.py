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

def list_type(s):
    return '<span class="list">%s %s<span class="comma">,</span> %s<span class="comma">,<span/> <span class="hellip">...</span> %s</span>' % (
        inline_brace('['),
        atomic_type(s),
        atomic_type(s),
        inline_brace(']'),
    )

def choice_values(values):
    return '<span class="choice">%s %s %s</span>' % (
        inline_brace('('),
        (' %s ' % inline_brace('|')).join(atomic_type(t) for t in values),
        inline_brace(')'),
    )


def block(s):
    return '<div class="block">%s</div>' % s

def line(s):
    return '<div>%s</div>' % (s)

def optional_line(s):
    return '<div class="optional">%s &nbsp; %s</div>' % (s, line_comment('optional'))

def block_comment(s):
    return '<div class="comment">// %s</div>' % s

def line_comment(s):
    return '<span class="comment">// %s</span>' % s

def propname(s):
    return '<span class="property">%s</span>' % s

def indent(*args):
    return '<div class="indent">%s</div>' % ''.join(args)

def format_hash(data, is_nested=False, add_line_if_not_exist=None):
    lines = []
    hash_items = data.items()
    if add_line_if_not_exist:
        hash_items.insert(0, add_line_if_not_exist)
    is_last = lambda i, last_i=len(hash_items) - 1: i == last_i
    for i, (key, value) in enumerate(sorted(hash_items,
        key=lambda (key, value): (
            isinstance(key, Optional),  # first non-optional
            not isinstance(value, basestring), # next just strings
            key,  # next abc-sorting
        )
    )):
#        if comment:
#            lines.append(block_comment(comment))
        if isinstance(key, Optional):
            lines.append(optional_line('%s %s%s' % (
                propname(safe(key.data) + ':'),
                format(value, nested_hash=True),
                '' if is_last(i) else '<span class="comma">,</span>'
            )))
        else:
            lines.append(line('%s %s%s' % (
                propname(safe(key) + ':'),
                format(value, nested_hash=True),
                '' if is_last(i) else '<span class="comma">,</span>'
            )))

    tail = indent(''.join(lines) or block_comment('empty')) + block_brace('}')
    if is_nested:
        return inline_brace('{') + tail
    else:
        return block_brace('{') + tail

def format(data, nested_hash=False, add_line_if_not_exist=None):
    if isinstance(data, basestring):
        return string(data)
    if isinstance(data, AnyOf):
        return OR(data.validators, add_line_if_not_exist)
    if isinstance(data, type):
        if data == bool:
            return choice_values(['true', 'false'])
        if data == int:
            return atomic_type(safe('integer'))
        else:
            return atomic_type(safe('!!!! type %s !!!' % data))
    if isinstance(data, list):
        assert len(data) == 1
        return list_type(format(data[0]))
    if isinstance(data, Text):
        return atomic_type(safe('string'))
    if isinstance(data, Positive):
        return atomic_type(safe('positive integer'))
    if isinstance(data, dict):
        #print 'data', data
        return format_hash(data, nested_hash, add_line_if_not_exist)
    return block_comment('%s not supported' % safe(type(data)))
    #raise NotImplementedError('%s not supported' % type(data))

def safe(s):
    return str(s).replace('<', '&lt;').replace('>', '&gt;')

def OR(lst, add_line_if_not_exist=None):
    if len(lst) < 2:
        return block(format(lst[0], add_line_if_not_exist=add_line_if_not_exist))
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
def get_file(fname):
    return open(os.path.join(root, fname)).read()

# Useful for documentation generation
class DocItem(object):
    def __init__(self, api_call):
        self.name = api_call.name
        self.scheme = api_call.scheme
        self.description = api_call.description

        self.io_type = ''
        self.cleaned_name = self.name

        if '_' in self.name:
            cleaned_name, io_type = self.name.rsplit('_', 1)
            if io_type in ('request', 'response'):
                self.io_type = io_type
                self.cleaned_name = cleaned_name

#def mix_action_name():

def generate_by_protocol(protocol, title='Untitled'):
    protocol = map(DocItem, protocol)

    requests =  [c for c in protocol if c.io_type == 'request']
    responses = [c for c in protocol if c.io_type == 'response']
    other =     [c for c in protocol if not c.io_type]

    items = []
    html_ids = []
    for req, resp in zip(requests, responses):
        assert req.cleaned_name == resp.cleaned_name
        req_id = req.name
        resp_id = resp.name
        html_ids += [req_id, resp_id]
        items.append('<div class="item">'
            '<h2>%(common_title)s</h2>'
            '<p>%(common_description)s</p>'
            '''<p><span class="pseudolink" onclick="showHide('%(req_id)s')">request</span></p>'''
            '<div class="io-input" id="%(req_id)s" style="display:none">'
                '%(req_scheme)s'
            '</div>'
            '''<p><span class="pseudolink" onclick="showHide('%(resp_id)s')">response</span></p>'''
            '<div class="io-output" id="%(resp_id)s" style="display:none">'
                '%(resp_scheme)s'
            '</div>'
        '</div>' % {
            'common_title': req.cleaned_name,
            'common_description': req.description,
            'req_id': req_id,
            'resp_id': resp_id,
            'req_scheme': format(req.scheme,
                add_line_if_not_exist=('action', req.cleaned_name)),
            'resp_scheme': format(resp.scheme),
        })

    for c in other:
        id = c.name
        html_ids += [id]
        items.append('<div class="item">'
            '<h2>%(title)s</h2>'
            '<p>%(description)s</p>'
            '''<p><span class="pseudolink" onclick="showHide('%(id)s')">show/hide</span></p>'''
            '<div class="io-output" id="%(id)s" style="display:none">'
                '%(scheme)s'
            '</div>'
        '</div>' % {
            'title': c.name,
            'description': c.description,
            'scheme': format(c.scheme),
            'id': id,
        })

    core = '<ol>%s</ol>' % ''.join('<li>%s</li>' % li for li in items)

    return (
        '<!DOCTYPE html>'
        '<html>'
            '<!-- generated -->'
            '<head>'
                '<title>'
                    '%(title)s'
                '</title>'
                '<style>'
                    '%(css)s'
                '</style>'
                '<script>'
                    '%(js)s'
                '</script>'
            '</head>'
        '<body>'
            '<div class="json-docs">'
                '<h1>%(title)s</h1>'
                '<p class="intro"><span class="pseudolink" onclick="showHideAll(%(ids)s)">Show/hide all</span></p>'
                '%(core)s'
            '</div>'
            '<script>showHideAll(%(ids)s);</script>'
        '</body>'
        '</html>' % {
            'title': title,
            'core': core,
            'css': get_file('json-docs.css'),
            'js': '\n'.join([get_file('json-docs.js'), get_file('javascript-1.6.js')]),
            'ids':  repr(html_ids),  # js arrays syntax = python list syntax
        }
    )

