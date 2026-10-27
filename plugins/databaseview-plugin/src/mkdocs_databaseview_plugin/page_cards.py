"""Fixed-size page cards for the supported native Bases cards view."""
from html import escape

from .book_cards import cover_url


DEFAULT_HEADER_IMAGE = 'https://bugsblog.neocities.org/cabbypics/Screenshot%202026-07-22%20223828.png'


def render_page_cards(rows, image_property, href_for_note, card_size, aspect_ratio, image_fit):
    if not rows:
        return '<p class="rv-page-cards-empty">No pages in this category yet.</p>\n'
    output = [f'<ul class="rv-page-cards" role="list" style="--rv-card-width:{card_size}px;'
              f'--rv-card-aspect:{aspect_ratio};--rv-card-fit:{image_fit}">']
    for note in rows:
        title = escape(note['name'], quote=True)
        href = escape(href_for_note(note['path']), quote=True)
        image = cover_url(note['properties'].get(image_property)) or DEFAULT_HEADER_IMAGE
        output.append(
            f'<li class="rv-page-card"><a class="rv-page-card__link" href="{href}" title="{title}">'
            f'<span class="rv-page-card__image"><img src="{escape(image, quote=True)}" alt="" '
            'loading="lazy" decoding="async" referrerpolicy="no-referrer"></span>'
            f'<span class="rv-page-card__title">{title}</span></a></li>'
        )
    output.append('</ul>')
    return '\n'.join(output) + '\n'
