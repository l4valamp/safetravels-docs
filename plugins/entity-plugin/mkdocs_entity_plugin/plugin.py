import re

from mkdocs.plugins import BasePlugin


class EntityPlugin(BasePlugin):

    def on_page_markdown(self, markdown, **kwargs):

        pattern = r"\{\{(.*?)(?::(.*?))?\}\}"

        def replace(match):

            entity = match.group(1).strip()

            # If no type is provided, use default
            variable_type = match.group(2)

            if variable_type:
                variable_type = variable_type.strip()
            else:
                variable_type = "default"

            return (
                f'<span class="entity entity-{variable_type}" '
                f'data-entity="{entity}" '
                f'data-type="{variable_type}">'
                f'{entity}'
                '</span>'
            )

        return re.sub(pattern, replace, markdown)
