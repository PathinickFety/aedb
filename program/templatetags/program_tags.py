from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_names):
    """Check if user belongs to any of the specified groups."""
    if not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    group_list = [name.strip() for name in group_names.split(',')]
    return user.groups.filter(name__in=group_list).exists()