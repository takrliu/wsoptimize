from django import template
register = template.Library()

@register.filter
def keyvalue(dictionary, key):   
	try:
		return dictionary[key]
	except KeyError:
		return ''