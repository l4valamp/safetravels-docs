1. Documents, project, project folder, open in visual studio code
2. Add files to visual studio code
3. Open terminal from Visual Studio Code
4. Create the virtual environment
```
python -m venv .venv
```

```
.venv\Scripts\activate
```

```
pip install mkdocs mkdocs-material
```

Later, install plugin 

```
pip install -e .
```

Virtual environment is a collection of packages. if all computer packages were global, they would conflict. 

Python packages cannot contain hyphens.

```
__init__.py
```

```
from mkdocs.plugins import BasePlugin


class EntityPlugin(BasePlugin):
    pass
```

import- I want to use MkDoc's plugin system

class = everything after this belongs to the plugin

pass = empty plugin

plugins receive "hooks" from MkDocs in the building process. replace "pass" with 

```
def on_page_markdown(self, markdown, **kwargs):
    return markdown
```

This says whenever MkDocs loads a page, give me the markdown as a string. 

import re at the beginning. re stands for regular expressions. re is tool for searching and replacing patterns in text. 

mkdocs sends pages to plugins and accepts modified pages back. 

Built-in python libraries first, third-party libraries second, our code last. 

NEXT STEP: Creating pyproject.toml. This turns folder of python code into installable Python package. 
A toml file is a configuration file format. (Settings)

pip = Python Package installer
-e = editable. Can edit plugin without reinstalling it every time.
. = this folder. 

THEN try installing it on a site.

{{EnginePower:float}} and then {{AnotherTest:string}} and {{EnginePower:float}} tada
{{EnginePower}} hello


Rendering Variables with Snippets. 

2 phases. 
1. Collect all definitions
2. Render all variables. 
EntityDefinitionProcessor is doing both at once. 