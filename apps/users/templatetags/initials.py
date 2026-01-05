from django import template

register = template.Library()

@register.filter(name='initials')
def initials(name: str):
    if not name:
        return ""
    
    words: str = name.strip().split()
    
    return (words[0][0] + (words[-1][0] if len(words) > 1 else "")).upper()
    
    