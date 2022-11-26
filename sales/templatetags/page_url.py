from django import template
register = template.Library()


@register.simple_tag
def url_replace(request, field, value):
    """GETパラメータを一部を置き換える"""

    url_dict = request.GET.copy()
    url_dict[field] = str(value)
    #url_dict['customer_name'] = str('a')
    #print(url_dict)
    return url_dict.urlencode()