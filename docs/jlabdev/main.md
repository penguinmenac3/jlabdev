[Back to Overview](../README.md)

> **The MIT License (MIT)**
> 
> Copyright (c) 2020 Michael Fuerst
> 
> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this software and associated documentation files (the "Software"), to deal
> in the Software without restriction, including without limitation the rights
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so, subject to the following conditions:
> 
> The above copyright notice and this permission notice shall be included in all
> copies or substantial portions of the Software.
> 
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
> IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
> FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
> AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
> LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
> OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
> SOFTWARE.

# jlabdev - Convert `.ipynb` to `.py` and generate `.md`-docs

> This tool allows conversion from an ipynb notebook into .py or .md files.

With the final tool there are 4 commands available:
* `nb2all` (see notebook2all): Call nb2py and nb2doc after each other.
* `nb2py` (see notebook2py): Generate python files for the jupyter notebooks.
* `nb2doc` (see notebook2doc): Generate markdown documentation for jupyter notebooks and python files.
* `py2nb` (see python2nb): Update the jupyter notebooks based on changes in the autogenerated python files.

---

## Finding Files

First we will implement a helper function that allows us to find all notebooks and another helper, that gets us all the all the pure python code and code that is generated from notebooks.

For that we will:
1. Find all files in the folder and subfolders.
2. Filter those which end on `.ipynb` as they are notebooks.
3. Filter for files which end on `.py` and are not in notebooks list.
4. Filter for files which end on `.py` and are in notebooks list.

## *class* **Files**(object) [[src]](../../jlabdev/main.py#L71)
*(no documentation found)*

### *def* **get_files** [[src]](../../jlabdev/main.py#L73)
*(no documentation found)*

### *def* **get_notebooks** [[src]](../../jlabdev/main.py#L95)
*(no documentation found)*

### *def* **get_pure_python_files** [[src]](../../jlabdev/main.py#L101)
*(no documentation found)*

### *def* **get_generated_python_files** [[src]](../../jlabdev/main.py#L108)

Example:
```python
print(Files.get_notebooks())
print(Files.get_pure_python_files())
print(Files.get_generated_python_files())
```

Output:
```
['jlabdev/main.ipynb']
['setup.py', 'jlabdev/__init__.py']
['jlabdev/main.py']
```

---

## Classifying Notebook Cells

A notebook is a json file with a list of cells of different types (e.g. code and markdown).
Cells wich start with a comment of `#export` will be converted and any notebook containing these cells will be convertible.

So first we want to write a set of helper functions to identify the different types of cells that we will later modify.

## *class* **Cell**(object) [[src]](../../jlabdev/main.py#L129)
*(no documentation found)*

### *def* **is_code_export** [[src]](../../jlabdev/main.py#L135)
*(no documentation found)*

### *def* **is_code_example** [[src]](../../jlabdev/main.py#L139)
*(no documentation found)*

### *def* **is_md_export** [[src]](../../jlabdev/main.py#L147)

---

## Converting Notebook to Python

To convert the notebook to python, we first load it and then collect all code and documentation cells and merge them into a single code string that is written next to the notebook.

## *class* **Notebook**(dict) [[src]](../../jlabdev/main.py#L162)
*(no documentation found)*

### *def* **is_code_notebook** [[src]](../../jlabdev/main.py#L168)
*(no documentation found)*

### *def* **to_python** [[src]](../../jlabdev/main.py#L174)

Example:
```python
notebook = Notebook(Files.get_notebooks()[0])
print(notebook.is_code_notebook())
print(notebook.to_python())
```

Output:
```
True
True
```

The actual conversion code is very simple based on the conversion of a single notebook already implemented.
We simply find all notebooks and then convert them to python.

## *def* **notebook2py** [[src]](../../jlabdev/main.py#L216)
Convert all notebooks in the current working directory folder.

Example:
```python
notebook2py()
```

Output:
```
Converted 1 notebook(s) to python out of 1 total.
```

---

## Convert Python to Markdown Documentation

This is actually more complicated. For this we will go through the source code line by line and find classes and functions to then find any docstrings attached to them.

## *class* **PythonDoc**(object) [[src]](../../jlabdev/main.py#L239)
*(no documentation found)*

### *def* **extract** [[src]](../../jlabdev/main.py#L326)
*(no documentation found)*

### *def* **fix_paths** [[src]](../../jlabdev/main.py#L381)
*(no documentation found)*

### *def* **python_to_markdown** [[src]](../../jlabdev/main.py#L394)

---

## Convert Notebook to Markdown Documentation

Additionally to the regular python to markdown here we want to extract the examples from the notebook to add to the documentation. Examples are all code cells not annotated with `#hide` or `#export`.

## *class* **NotebookForDocumentation**(Notebook) [[src]](../../jlabdev/main.py#L432)
*(no documentation found)*

### *def* **is_example_notebook** [[src]](../../jlabdev/main.py#L433)
*(no documentation found)*

### *def* **to_markdown** [[src]](../../jlabdev/main.py#L517)

Example:
```python
notebook = NotebookForDocumentation(Files.get_notebooks()[0])
print(notebook.is_code_notebook())
print(notebook.to_markdown())
```

Output:
```
True
('jlabdev/main.md', 'jlabdev - Convert `.ipynb` to `.py` and generate `.md`-docs\n')
```

## *def* **notebook2doc** [[src]](../../jlabdev/main.py#L548)
Convert all notebooks in the folder.

Also converts notebooks annotated with #example in first cell.
All notebooks, which have a title starting with "Example: " are listed under examples without the "Example: " shown in the list.

* **project_root** *(str, optional)*: The root directory of the project. The default exp path is relative to this folder.

Example:
```python
notebook2doc()
```

Output:
```
Converted to md: jlabdev/main.ipynb
```

## *def* **notebook2all** [[src]](../../jlabdev/main.py#L595)
Run the notebook2py and notebook2doc commands.

* **project_root** *(str, optional)*: The path to the project root, defaults to ".".

Example:
```python
notebook2all()
```

Output:
```
Converted 1 notebook(s) to python out of 1 total.
Converted to md: jlabdev/main.ipynb
```

---

## Update notebook from python

## *def* **python2nb** [[src]](../../jlabdev/main.py#L666)
Convert all notebooks in the folder.

* **project_root** *(str, optional)*: The root directory of the project. The default exp path is relative to this folder.

