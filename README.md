# LatticeTools
Components for generating lattice structures with conformal, open skins in Rhino®/Grasshopper®, based on the methods presented in [_Scalable, process-oriented beam lattices: Generation, characterization, and compensation for open cellular structures_](https://doi.org/10.1016/j.addma.2021.102386).

*The content of this repository does not represent the views or official positions of any institutions or funding agencies associated with the authors or their respective affiliations.

# Usage

The primary utility of this plugin is in generating lattice structures for 3D printing that are open and self-supporting, along with relevant logs of the process.

This repository includes a demonstration script (`LatticeTools-Demo.gh`) and documentation for the components (`/documentation/latticetools.pdf`), as well as the full source. Feel free to explore them and contribute your feedback.

Install the plugin just like any other. Take a look at the documentation for more information.

# Development

The current state of these tools is designed to be compiled with the Script Editor in Rhino. To make new components or debug, create a ghpython component in Grasshopper, set up the inputs/outputs, and 

To have autocompletion when working with Rhino/Grasshopper functions, install the Python stubs from McNeel and reference them in your editor.

Refs:
- [https://github.com/mcneel/pythonstubs](https://github.com/mcneel/pythonstubs)
- [https://stevebaer.wordpress.com/2019/02/25/autocomplete-and-type-hints-with-python-scripts-for-rhino-grasshopper/](https://stevebaer.wordpress.com/2019/02/25/autocomplete-and-type-hints-with-python-scripts-for-rhino-grasshopper/)
- [https://discourse.mcneel.com/t/autocomplete-while-editing-python-scripts-outside-of-rhino/79329](https://discourse.mcneel.com/t/autocomplete-while-editing-python-scripts-outside-of-rhino/79329)

VS Code `settings.json`
```json
{
    "python.analysis.extraPaths": [
        "C:\\Users\\user\\AppData\\Roaming\\McNeel\\python-stubs",
        "C:\\Users\\user\\AppData\\Roaming\\McNeel\\Rhinoceros\\6.0\\Plug-ins\\IronPython (814d908a-e25c-493d-97e9-ee3861957f49)\\settings\\lib"
    ],
 "editor.rulers": [
        80,
        120
    ]
}
```