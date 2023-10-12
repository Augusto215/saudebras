from django import template
from urllib.parse import urlencode

register = template.Library()

@register.filter(name='add_page_to_query')
def add_page_to_query(query_dict, page_number):
    query = query_dict.copy()
    query['page'] = page_number
    return urlencode(query)
