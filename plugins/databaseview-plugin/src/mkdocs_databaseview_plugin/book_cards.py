"""Presentation of exported rows; Obsidian remains the query evaluator."""
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlsplit

import markdown


def cover_url(value):
    if not isinstance(value, str):
        return None
    value = value.strip()
    if not value or any(c.isspace() or ord(c) < 32 for c in value) or '\\' in value:
        return None
    try:
        parsed = urlsplit(value)
        if parsed.scheme.lower() not in ('http', 'https') or not parsed.hostname:
            return None
        parsed.port  # Reject malformed port numbers as well.
    except ValueError:
        return None
    return value


class ExportRows(HTMLParser):
    """Read table cells and group headings without trusting snapshot HTML."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.events = []
        self.row = None
        self.cell = None
        self.heading = None
        self.author_column = None

    def handle_starttag(self, tag, attrs):
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self.heading = []
        elif tag == 'table':
            self.author_column = None
        elif tag == 'tr':
            self.row = []
        elif tag in ('th', 'td') and self.row is not None:
            self.cell = {'text': [], 'href': None, 'header': tag == 'th'}
        elif tag == 'a' and self.cell is not None:
            self.cell['href'] = dict(attrs).get('href')
        elif tag == 'br' and self.cell is not None:
            self.cell['text'].append(' ')

    def handle_data(self, data):
        if self.heading is not None:
            self.heading.append(data)
        if self.cell is not None:
            self.cell['text'].append(data)

    def handle_endtag(self, tag):
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6') and self.heading is not None:
            self.events.append(('heading', ''.join(self.heading)))
            self.heading = None
        elif tag in ('th', 'td') and self.cell is not None:
            self.cell['text'] = ''.join(self.cell['text']).strip()
            self.row.append(self.cell)
            self.cell = None
        elif tag == 'tr' and self.row is not None:
            if any(cell['header'] for cell in self.row):
                self.author_column = next((i for i, cell in enumerate(self.row)
                                           if cell['text'].casefold() == 'author'), None)
            else:
                link = next((cell for cell in self.row if cell['href']), None)
                if link:
                    author = self.row[self.author_column]['text'] if self.author_column is not None and self.author_column < len(self.row) else ''
                    self.events.append(('book', (link['href'], link['text'], author)))
            self.row = None


def render_cards(snapshot, resolve):
    parser = ExportRows()
    parser.feed(markdown.markdown(snapshot, extensions=['tables']))
    output = []
    opened = False
    count = 0
    for kind, value in parser.events:
        if kind == 'heading':
            if opened:
                output.append('</ul>\n\n')
                opened = False
            # Markdown headings remain visible to MkDocs' TOC/anchor renderer.
            heading = escape(value)
            heading = ''.join('\\' + c if c in '\\`*_{}[]()#+-.!' else c for c in heading)
            output.append('### ' + heading + '\n\n')
            continue
        source, title, author = value
        href, cover = resolve(source)
        if not opened:
            output.append('<ul class="rw-book-grid">')
            opened = True
        image = (f'<img class="rw-book-image" src="{escape(cover, quote=True)}" alt="" '
                 'width="200" height="300" loading="lazy" decoding="async">') if cover else ''
        author_html = f'<span class="rw-book-author">{escape(author)}</span>' if author and author.casefold() not in ('null', 'undefined') else ''
        output.append(
            '<li class="rw-book-card">'
            f'<a class="rw-book-link" href="{escape(href, quote=True)}">'
            '<span class="rw-book-cover"><span class="rw-book-placeholder" aria-hidden="true"></span>'
            f'{image}</span><span class="rw-book-title">{escape(title)}</span>'
            f'{author_html}</a></li>')
        count += 1
    if opened:
        output.append('</ul>')
    if not count:
        output.append('<p class="rw-book-empty">No books in this view.</p>')
    return '\n'.join(output)
