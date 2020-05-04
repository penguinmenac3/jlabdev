# JLAB Dev

> Develop python packages using jupyterlab.

This library allows you to develop regular python packages while writing your code in jupyterlab.
You can create notebooks to develop your code and in these notebooks, simply annotate your cells with `#export` if you want them to be put in the library.
Other cells will be used as examples in your doc (together with the markdown of your notebook) unless marked with `#hide`.
You can specify the path of the package where to put the code by using `#default_exp mymodule.myclass`.

![Image of nb_convert notebook](images/ExampleNotebook.png)

Of course JLAB Dev itself is completly implemented as a notebook in jupyterlab.

## Installation

It is as simple as a pip install.

```bash
# For stable version
pip install jlabdev

# or for bleeding edge
pip install git+https://github.com/penguinmenac3/jlabdev.git
```

## Usage

### Basics

Simply create your notebooks and add a code cell with `#default_exp mymodule.myclass` to the top and annotate all cells you want to export with `#export`.

Now you can compile your notebook into python and markdown doc by saving it and then running the following 3 python lines with the home of your project as the working directory:

```pyhton
from jlabdev.nb_convert import notebook2py, notebook2md
notebook2py(project_root=".", nb_root="notebooks")
notebook2md(project_root=".", nb_root="notebooks")
```

### Readme and Documentation

In order to create the typical project readme, create a README_TEMPLATE.md in your notebook root folder. This Markdown can be structured as you want. However, the first occurance of `{toc}` will be automatically replaced by a table of content for the documentation (as in this readme under section documentation).

# Documentation

Here is a detailed documentation of all modules in jlabdev:

* [01. Convert Notebooks to *.py and *.md
](docs/jlabdev.nb_convert.md)



# License

The MIT License (MIT)

Copyright (c) 2020 Michael Fuerst

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
