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

        markdown = re.sub(pattern, replace, markdown)

         #
        # Pass 2 - Replace specific words
        #

        replacements = {
            "anna": "Anna(doomed)",
            "Greta": "COOL Greta",
            "Audrey": "Awdrey",
            "Carson": "Chunky P",
            "Chris": "CHRIS",
            "Daly": "Dally",
            "Kat": "Kart",
            "Riley": "Ruley",
            "Roan": "Rooan",
            "Cian": "Cian :3",
            "Marley": "Mawley",
            "Viv": "Vov",
            "Ajax": "A Jax",
            "Victoria": "Vee",
            "Vee": "V",
            "Jesse": "Je'sse",
        }

        for old, new in replacements.items():
            markdown = re.sub(rf"\b{re.escape(old)}\b", new, markdown, flags=re.IGNORECASE)

        return markdown