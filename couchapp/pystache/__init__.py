from couchapp.pystache.template import Template
from couchapp.pystache.view import View

def render(template, context=None, **kwargs):
    context = context and context.copy() or {}
    context.update(kwargs)
    return Template(template, context).render()
