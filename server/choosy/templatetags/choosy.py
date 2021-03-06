import re

from django import template
from django.template.defaultfilters import stringfilter
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode

import markdown as markdown_mod
import pygments

from desk.models import Exercise

register = template.Library()

@register.filter
@stringfilter
def markdown(value):
    """
    Runs Markdown over a given value.

    Syntax::

        {{ value|markdown }}

    """
    return mark_safe(markdown_mod.markdown(force_unicode(value), ["codehilite"], safe_mode="remove"))
markdown.is_safe = True


@register.filter
@stringfilter
def syntax_color(value):
    """Syntax-color a value with Pygments."""
    try:
        lexer = pygments.lexers.guess_lexer(value)
    except ValueError:
        lexer = pygments.lexers.PythonLexer()
    return mark_safe(pygments.highlight(force_unicode(value), lexer, pygments.formatters.HtmlFormatter()))
syntax_color.is_safe = True


@register.filter
@stringfilter
def embed_exercises(value):
    """Find [ex:slug] paragraphs, and embed them."""
    def get_exercise(m):
        slug = m.group('slug')
        try:
            ex = Exercise.objects.get(slug=slug)
        except Exercise.DoesNotExist:
            return "<p><b>Exercise %s not found!</b></p>" % (slug,)

        return render_to_string("gym/templates/oneexercise.html", {'ex': ex})

    value = re.sub(r"<p>\[ex:\s*(?P<slug>\w+)\s*]</p>", get_exercise, value)
    return value
embed_exercises.is_safe = True
