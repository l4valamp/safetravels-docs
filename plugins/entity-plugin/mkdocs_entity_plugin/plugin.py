import re

from mkdocs.plugins import BasePlugin


class EntityPlugin(BasePlugin):

    def on_page_markdown(self, markdown, **kwargs):

        definitions = {}

        #
        # Pass 1 - Collect variable definitions
        #
        # Syntax:
        # {{!Name:type:scope:"Description"}}
        #

        definition_pattern = re.compile(
            r'\{\{!([^}:]+)(?::([^}:]+))?(?::([^}:]+))?(?::"([^"]*)")?\}\}'
        )

        def collect_definition(match):

            entity = match.group(1).strip()

            variable_type = (
                match.group(2).strip()
                if match.group(2)
                else "default"
            )

            scope = (
                match.group(3).strip()
                if match.group(3)
                else "default"
            )

            description = (
                match.group(4).strip()
                if match.group(4)
                else ""
            )

            definitions[entity] = {
                "type": variable_type,
                "scope": scope,
                "description": description,
            }

            #
            # Return the same variable syntax without !
            # so Pass 2 can process it normally
            #

            return (
                f"{{{{{entity}:{variable_type}:{scope}}}}}"
            )


        markdown = definition_pattern.sub(
            collect_definition,
            markdown
        )


        #
        # Pass 2 - Replace entity references
        #

        pattern = re.compile(
            r"\{\{([^}:]+)(?::([^}:]+))?(?::([^}:]+))?\}\}"
        )


        def replace(match):

            entity = match.group(1).strip()

            variable_type = (
                match.group(2).strip()
                if match.group(2)
                else "default"
            )

            scope = (
                match.group(3).strip()
                if match.group(3)
                else "default"
            )

            description = ""

            if entity in definitions:
                description = definitions[entity]["description"]


            return (
                f'<span '
                f'class="entity entity-{variable_type} '
                f'entity-scope-{scope}" '
                f'data-entity="{entity}" '
                f'data-type="{variable_type}" '
                f'data-scope="{scope}" '
                f'data-description="{description}">'
                f'{entity}'
                f'</span>'
            )


        markdown = pattern.sub(
            replace,
            markdown
        )


        #
        # Pass 3 - Replace specific words
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
            markdown = re.sub(
                rf"\b{re.escape(old)}\b",
                new,
                markdown,
                flags=re.IGNORECASE,
            )


        return markdown
