# AUTOGENERATED FROM: jlabdev/main.ipynb


#%% Cell: 0
"""doc
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
"""


#%% Cell: 1
"""doc
# jlabdev - Convert `.ipynb` to `.py` and generate `.md`-docs

> This tool allows conversion from an ipynb notebook into .py or .md files.

With the final tool there are 4 commands available:
* `nb2all` (see notebook2all): Call nb2py and nb2doc after each other.
* `nb2py` (see notebook2py): Generate python files for the jupyter notebooks.
* `nb2doc` (see notebook2doc): Generate markdown documentation for jupyter notebooks and python files.
* `py2nb` (see python2nb): Update the jupyter notebooks based on changes in the autogenerated python files.
"""


#%% Cell: 2
from typing import List, Dict, Optional
import json
import os
import sys
import hashlib
import shutil
import base64


#%% Cell: 3
"""doc
---

## Finding Files

First we will implement a helper function that allows us to find all notebooks and another helper, that gets us all the all the pure python code and code that is generated from notebooks.

For that we will:
1. Find all files in the folder and subfolders.
2. Filter those which end on `.ipynb` as they are notebooks.
3. Filter for files which end on `.py` and are not in notebooks list.
4. Filter for files which end on `.py` and are in notebooks list.
"""


#%% Cell: 4
class Files(object):
    @staticmethod
    def get_files() -> List[str]:
        def _join_path_cleanly(root, fname):
            joined_path = os.path.join(root, fname)
            linux_style_path = joined_path.replace("\\", "/")
            root_free_path = linux_style_path.replace("./", "")
            return root_free_path

        file_paths = []
        for root, dirs, files in os.walk("."):
            out_dirs = []
            for folder in dirs:
                current_dir = root.split(os.sep)[-1]
                if not current_dir.startswith(".") or current_dir == ".":
                    out_dirs.append(folder)
            dirs[:] = out_dirs
            if ".ipynb_checkpoints" in root:
                continue
            for f in files:
                file_paths.append(_join_path_cleanly(root, f))
        return file_paths

    @staticmethod
    def get_notebooks() -> List[str]:
        def _is_notebook(file_name):
            return file_name.endswith(".ipynb")
        return list(filter(_is_notebook, Files.get_files()))

    @staticmethod
    def get_pure_python_files() -> List[str]:
        notebooks = Files.get_notebooks()
        def _is_pure_python(file_name):
            return file_name.endswith(".py") and file_name.replace(".py", ".ipynb") not in notebooks
        return list(filter(_is_pure_python, Files.get_files()))

    @staticmethod
    def get_generated_python_files() -> List[str]:
        notebooks = Files.get_notebooks()
        def _is_generated_from_notebook(file_name):
            return file_name.endswith(".py") and file_name.replace(".py", ".ipynb") in notebooks
        return list(filter(_is_generated_from_notebook, Files.get_files()))


#%% Cell: 5
"""doc
---

## Classifying Notebook Cells

A notebook is a json file with a list of cells of different types (e.g. code and markdown).
Cells wich start with a comment of `#export` will be converted and any notebook containing these cells will be convertible.

So first we want to write a set of helper functions to identify the different types of cells that we will later modify.
"""


#%% Cell: 6
class Cell(object):
    @staticmethod
    def _is_non_empty_code_cell(cell) -> bool:
        return cell["cell_type"] == "code" and len(cell["source"]) > 0

    @staticmethod
    def is_code_export(cell) -> bool:
        return Cell._is_non_empty_code_cell(cell) and cell["source"][0].startswith("#export")

    @staticmethod
    def is_code_example(cell) -> bool:
        return Cell._is_non_empty_code_cell(cell) and not cell["source"][0].startswith("#hide") and not cell["source"][0].startswith("#export")

    @staticmethod
    def _is_non_empty_markdown_cell(cell) -> bool:
        return cell["cell_type"] == "markdown" and len(cell["source"]) > 0

    @staticmethod
    def is_md_export(cell) -> bool:
        return Cell._is_non_empty_markdown_cell(cell) and not cell["source"][0].startswith("#hide") and not cell["source"][0].startswith("<!-- hide -->")


#%% Cell: 7
"""doc
---

## Converting Notebook to Python

To convert the notebook to python, we first load it and then collect all code and documentation cells and merge them into a single code string that is written next to the notebook.
"""


#%% Cell: 8
class Notebook(dict):
    def __init__(self, file_path: str):
        with open(file_path, "r", encoding="utf8") as f:
            super().__init__(json.loads(f.read()))
        self.file_path = file_path

    def is_code_notebook(self) -> bool:
        for cell in self["cells"]:
            if Cell.is_code_export(cell):
                return True
        return False

    def to_python(self) -> bool:
        if not self.is_code_notebook():
            return False

        code_cells = ["# AUTOGENERATED FROM: {}".format(self.file_path)]
        for cell in self["cells"]:
            cell_idx = len(code_cells) - 1
            if Cell.is_code_export(cell):
                code = "".join(cell["source"])
                code = code.replace("#export", f"#%% Cell: {cell_idx}", 1)
                while code.endswith("\n"):
                    code = code[:-2]
                code_cells.append(code)
            elif Cell.is_md_export(cell):    
                code = f"#%% Cell: {cell_idx}\n"
                code += "\"\"\"doc\n" # start doc comment
                code += "".join(cell["source"])
                while code.endswith("\n"):
                    code = code[:-2]
                code += "\n\"\"\""
                code_cells.append(code)
            else:
                continue
        
        # One new line for inside cell and then two empty lines
        # Add another newline at the end of the document
        code = "\n\n\n".join(code_cells) + "\n"

        with open(self.file_path.replace(".ipynb", ".py"), "w", encoding="utf8") as f:
            f.write(code)
        
        return True


#%% Cell: 9
"""doc
The actual conversion code is very simple based on the conversion of a single notebook already implemented.
We simply find all notebooks and then convert them to python.
"""


#%% Cell: 10
def notebook2py() -> None:
    """Convert all notebooks in the current working directory folder.
    """
    notebooks = Files.get_notebooks()
    converted = 0
    for file_path in notebooks:
        notebook = Notebook(file_path)
        if notebook.to_python():
            converted += 1
    print(f"Converted {converted} notebook(s) to python out of {len(notebooks)} total.")


#%% Cell: 11
"""doc
---

## Convert Python to Markdown Documentation

This is actually more complicated. For this we will go through the source code line by line and find classes and functions to then find any docstrings attached to them
"""


#%% Cell: 12
class PythonDoc(object):
    @staticmethod
    def _is_definition(line):
        return (line.startswith("def ") or line.startswith("class ")) and not (line.startswith("def _") or line.startswith("class _"))

    @staticmethod
    def _add_separator(doc):
        doc.append("\n\n")

    @staticmethod
    def _common_header(indent, def_type, name, superclass=""):
        level = int(indent / 4) + 1
        header_style = "#" + ("#"*level)
        return f"{header_style} *{def_type}* **{name}**{superclass}"

    @staticmethod
    def _add_class_doc_header(doc, line, indent):
        superclass = ""
        if "(" in line:
            name, superclass = line.split(" ")[1].split("(")
            superclass = "(" + superclass.split(")")[0] + ")"
        else:
            name = line.split(" ")[1].split(":")[0]
        doc.append(PythonDoc._common_header(indent, "class", name, superclass))
    
    @staticmethod
    def _add_def_doc_header(doc, line, indent):
        fun_name, args = line.split(" ")[1].split("(")
        doc.append(PythonDoc._common_header(indent, "def", fun_name))
    
    @staticmethod
    def _add_code_link(doc, source_path_relative, line_idx):
        if source_path_relative is not None:
            doc[-1] += f" [[src]]({source_path_relative}#L{line_idx+1})"

    @staticmethod
    def _add_object_doc_start(doc, line):
        line = line[3:]
        if line.rstrip().endswith("\"\"\""):
            PythonDoc._add_doc_string(doc, line[:-3].lstrip().rstrip())
            return False
        else:
            line = line.lstrip().rstrip()
            if line != "":
                PythonDoc._add_doc_string(doc, line)
            return True

    @staticmethod
    def _add_doc_end(doc, line):
        line = line[:-3].rstrip()
        if line != "":
            PythonDoc._add_doc_string(doc, line)

    @staticmethod
    def _add_doc_string(doc, line):
        if line.lstrip().startswith(":param"):
            line = line.replace(":param ", "* **")
            end_of_param = line.index(":")
            doc.append(line[:end_of_param] + "**" + line[end_of_param:])
        # If there is a type parameter amend the last param line and add types.
        elif line.lstrip().startswith(":type"):
            line = line.replace(":type ", "")
            end_of_param = line.index(":")
            param_name = line[:end_of_param]
            param_type = line[(end_of_param+1):].lstrip().rstrip()
            old_param_header = f"* **{param_name}**:"
            if old_param_header in doc[-1]:
                new_param_header = f"* **{param_name}** *({param_type})*:"
                doc[-1] = doc[-1].replace(old_param_header, new_param_header)
            else:
                print("ERROR: Invalid doc format, ':param X:' must come before ':type X:'.")
        # :return: is an easy replace.
        elif line.lstrip().startswith(":return:"):
            doc.append(line.replace(":return:", "* **returns**:"))
        # If there is a return type amend the last line and add types.
        elif line.lstrip().startswith(":rtype:"):
            line = line.replace(":rtype:", "").lstrip().rstrip()
            old_param_header = f"* **returns**:"
            if doc[-1].startswith(old_param_header):
                new_param_header = f"* **returns** *({line})*:"
                doc[-1] = doc[-1].replace(old_param_header, new_param_header)
            else:
                print("ERROR: Invalid doc format, ':return:' must come before ':rtype:'.")
        else:
            doc.append(line)

    @staticmethod
    def extract(source:str, source_path_relative:str = None, global_line_offset: int = 0) -> str:
        state_reading_docstring = False
        state_expecting_docstring = False
        state_reading_string = False

        doc = []
        current_doc_indentation = 0
        for line_idx, orig_line in enumerate(source.split("\n")):
            line = orig_line.lstrip()
            if "\"\"\"" in line:
                state_reading_string = not state_reading_string
            indent = len(orig_line) - len(line)
            if not state_reading_docstring:
                if PythonDoc._is_definition(line):
                    if state_expecting_docstring:
                        doc.append("*(no documentation found)*")
                    if line.startswith("class "):
                        PythonDoc._add_separator(doc)
                        PythonDoc._add_class_doc_header(doc, line, indent)
                    elif line.startswith("def "):
                        PythonDoc._add_separator(doc)
                        PythonDoc._add_def_doc_header(doc, line, indent)
                    else:
                        raise RuntimeError(f"This case should not happen. Cannot understad type of line: {line}")
                    PythonDoc._add_code_link(doc, source_path_relative, line_idx + global_line_offset)
                    state_expecting_docstring = True
                elif state_reading_string and line.startswith("\"\"\"doc"):
                    # Start module docstring """doc
                    if state_expecting_docstring:
                        doc.append("*(no documentation found)*")
                    state_expecting_docstring = False
                    current_doc_indentation = indent
                    PythonDoc._add_separator(doc)
                    state_reading_docstring = True
                elif state_expecting_docstring and state_reading_string and line.startswith("\"\"\""):
                    # Start docstring for function/class """
                    state_expecting_docstring = False
                    current_doc_indentation = indent
                    state_reading_docstring = PythonDoc._add_object_doc_start(doc, line)
            elif state_reading_docstring:
                if "\"\"\"" in line:
                    if not line.rstrip().endswith("\"\"\""):
                        print("WARNING: Your last documentation line should close with \"\"\" doc might be truncated or broken.")
                    state_reading_docstring = False  # Close the open docstring
                    PythonDoc._add_doc_end(doc, orig_line[current_doc_indentation:])
                else:
                    PythonDoc._add_doc_string(doc, orig_line[current_doc_indentation:].rstrip())

        doc = "\n".join(doc) + "\n"

        while "\n\n\n" in doc:
            doc = doc.replace("\n\n\n", "\n\n")

        return doc.lstrip()

    def fix_paths(output):
        start = 0
        idx = output.find("![", start)
        while idx >= 0:
            left = output.find("](", idx)
            if left != output.find("](data:", idx):
                output = output[:left] + "](../" + output[left+2:]
            start = idx + 1
            idx = output.find("![", start)
        return output

    # TODO make cleaner
    @staticmethod
    def python_to_markdown(file_path) -> str:
        with open(file_path, "r") as f:
            source = f.readlines()
        title = None
        for idx, line in enumerate(source):
            if line.startswith("\"\"\"doc"):
                if source[idx+1].startswith("# "):
                    title = source[idx+1][2:-1]
                    break
        if title is None:
            return None, None

        md_name = file_path.replace(".py", ".md")
        md_path = os.path.join("docs", md_name).replace("\\", "/")
        base_path_relative = "/".join([".." for _ in range(len(md_name.split("/"))-1)])
        source_path_relative = os.path.join("..", base_path_relative, md_name.replace(".md", ".py"))
        doc = "[Back to Overview]({})\n\n".format(base_path_relative + "/README.md")
        doc += PythonDoc.extract("".join(source), source_path_relative)
        doc = PythonDoc.fix_paths(doc)

        path = "/".join(md_path.split("/")[:-1])
        os.makedirs(path, exist_ok=True)
        with open(md_path, "w", encoding="utf8") as f:
            f.write(doc)
        return md_name, title


#%% Cell: 13
"""doc
---

## Convert Notebook to Markdown Documentation

Additionally to the regular python to markdown here we want to extract the examples from the notebook to add to the documentation. Examples are all code cells not annotated with `#hide` or `#export`.
"""


#%% Cell: 14
class NotebookForDocumentation(Notebook):
    def is_example_notebook(self) -> bool:
        if Notebook.is_code_notebook(self):
            return False
        for cell in self["cells"]:
            if Cell.is_md_export(cell) and (cell["source"][0].startswith("# Example") or cell["source"][0].startswith("#Example")):
                return True
        return False

    def _extract_doc(self, base_path_relative, py_name) -> str:
        source_path_relative = None
        py_code = None
        if os.path.exists(py_name):
            source_path_relative = os.path.join("..", base_path_relative, self.file_path.replace(".ipynb", ".py"))
            with open(py_name, "r") as f:
                py_code = f.read().split("\n")

        doc = "[Back to Overview]({})\n\n".format(base_path_relative + "/README.md")
        images = {}
        title = None
        cell_idx = 0
        for cell in self["cells"]:
            # Example Cell
            if cell["cell_type"] == "code" and len(cell["source"]) > 0 and not cell["source"][0].startswith("#export") and not cell["source"][0].startswith("#hide") and not cell["source"][0].startswith("#convert") and not cell["source"][0].startswith("#example"):
                doc += "\nExample:\n"
                doc += "```python\n"
                for line in cell["source"]:
                    doc += line
                doc += "\n```\n"
                image_data = []
                outp_text = ""
                for outp in cell["outputs"]:
                    if "text" in outp:
                        for entry in outp["text"]:
                            outp_text += entry
                    if "data" in outp:
                        if "image/png" in outp["data"]:
                            image_data.append(outp["data"]["image/png"])
                    if "traceback" in outp:
                        for entry in outp["traceback"]:
                            while entry.find('\x1b') >= 0:
                                start = entry.find('\x1b')
                                end = entry.find("m", start)
                                entry = entry[:start] + entry[end+1:]
                            outp_text += entry + "\n"

                if outp_text != "":
                    doc += "\nOutput:\n"
                    doc += "```\n"
                    doc += outp_text
                    doc += "```\n"
                for img in image_data:
                    md5 = hashlib.md5(img.encode('utf-8')).hexdigest()
                    with open("docs/jlabdev_images/{}.png".format(md5), "wb") as fh:
                        
                        fh.write(base64.b64decode(img))
                    doc +="![data](" + base_path_relative + "/docs/jlabdev_images/{}.png)\n".format(md5)
                doc += "\n\n"

            # Export Cell
            if Cell.is_code_export(cell):
                source = "".join(cell["source"])
                global_line_offset = -1
                for line_idx, line in enumerate(py_code):
                    if line.lstrip().rstrip() == f"#%% Cell: {cell_idx}":
                        global_line_offset = line_idx
                doc += PythonDoc.extract(source, source_path_relative, global_line_offset) + "\n"

            # Regular Markdown Cell
            if Cell.is_md_export(cell):
                for line in cell["source"]:
                    if line.startswith("# ") and title is None:
                        title = line[2:]
                    doc += line
                doc += "\n\n"

            if Cell.is_code_export(cell) or Cell.is_md_export(cell):
                cell_idx += 1
        
        doc += "\n"
        while "\n\n\n" in doc:
            doc = doc.replace("\n\n\n", "\n\n")
        
        return doc.lstrip(), title

    def to_markdown(self) -> str:
        if not self.is_code_notebook() and not self.is_example_notebook():
            return None, None
        
        md_name = self.file_path.replace(".ipynb", ".md")
        py_name = self.file_path.replace(".ipynb", ".py")

        md_path = os.path.join("docs", md_name).replace("\\", "/")
        base_path_relative = "/".join([".." for _ in range(len(md_name.split("/"))-1)])
        doc, title = self._extract_doc(base_path_relative, py_name)
        doc = PythonDoc.fix_paths(doc)

        path = "/".join(md_path.split("/")[:-1])
        os.makedirs(path, exist_ok=True)
        with open(md_path, "w", encoding="utf8") as f:
            f.write(doc)
        return md_name, title


#%% Cell: 15
DOC_INDEX_TEMPLATE = """
# Examples

{examples}

# Documentation

{toc}

"""

def notebook2doc(readme_template=None) -> None:
    """Convert all notebooks in the folder.

    Also converts notebooks annotated with #example in first cell.
    All notebooks, which have a title starting with "Example: " are listed under examples without the "Example: " shown in the list.
    
    :param project_root: The root directory of the project. The default exp path is relative to this folder.
    :type project_root: str, optional
    """
    if readme_template is None:
        readme_template = DOC_INDEX_TEMPLATE
    notebooks = Files.get_notebooks()
    non_notebooks = Files.get_pure_python_files()
    index = []
    shutil.rmtree("docs")
    os.makedirs(os.path.join("docs", "jlabdev_images"))
    for nb_path in notebooks:
        nb = NotebookForDocumentation(nb_path)
        name, title = nb.to_markdown()
        if name is not None:
            print("Converted to md: {}".format(nb_path))
            index.append((name, title))
    for py_path in non_notebooks:
        name, title = PythonDoc.python_to_markdown(py_path)
        if name is not None:
            print("Converted to md: {}".format(py_path))
            index.append((name, title))
    
    index = sorted(index, key=lambda x: x[1])
    
    if len(index) > 0:
        with open(os.path.join("docs", "README.md"), "w", encoding="utf8") as f:
            toc = ""
            examples = ""
            for i in index:
                if i[1].startswith("Example: "):
                    examples += "* [{}]({})\n".format(i[1].replace("Example: ", ""), i[0])
                else:
                    toc += "* [{}]({})\n".format(i[1], i[0])

            if examples == "":
                examples = "(no examples found)"
            readme_template = readme_template.replace("`{toc}`", "`#toc%`").format(toc=toc, examples=examples).replace("`#toc%`", "`{toc}`")
            f.write(readme_template)


#%% Cell: 16
def notebook2all() -> None:
    """Run the notebook2py and notebook2doc commands.

    :param project_root: The path to the project root, defaults to ".".
    :type project_root: str, optional
    """
    notebook2py()
    notebook2doc()


#%% Cell: 17
"""doc
---

## Update notebook from python
"""


#%% Cell: 18
def _get_py_cells(py_file):
    with open(py_file, "r", encoding="utf8") as f:
        data = f.read()
    if not data.startswith("# AUTOGENERATED FROM: "):
        return None, None
    
    lines = data.split("\n")
    file_path = lines[0].replace("# AUTOGENERATED FROM: ", "")
    cells = []
    current_cell = []
    header = True
    for line in lines:
        if line.startswith("#%% Cell:"):
            if not header:
                cells.append(current_cell)
            header = False
            current_cell = []
            continue
        if not header:
            current_cell.append(line)
    if not header:
        cells.append(current_cell)
    for i in range(len(cells)):
        cells[i] = "\n".join(cells[i])
        while cells[i].endswith("\n"):
            cells[i] = cells[i][:-1]
        cells[i] = cells[i].split("\n")
        for idx in range(len(cells[i]) -1):
            cells[i][idx] += "\n"
    return file_path, cells


#%% Cell: 19
def _overwrite_exported_cells(data, cells):
    i = 0
    for cell in data["cells"]:
        if Cell.is_code_export(cell):
            cell["source"] = ["#export\n"] + cells[i]
            i += 1
        if Cell.is_md_export(cell):
            cells[i][-2] = cells[i][-2][:-1]
            cell["source"] = cells[i][1:-1]
            i += 1


#%% Cell: 20
def _save_notebook(file_path: str, notebook: Dict) -> None:
    with open(file_path, "w", encoding="utf8") as f:
        return f.write(json.dumps(notebook, indent=1) + "\n")


#%% Cell: 21
def python2nb() -> None:
    """
    Convert all notebooks in the folder.
    
    :param project_root: The root directory of the project. The default exp path is relative to this folder.
    :type project_root: str, optional
    """
    readme_template = DOC_INDEX_TEMPLATE
    pyfiles = Files.get_generated_python_files()
    index = []
    for py_path in pyfiles:
        print("Converting to notebook: {}".format(py_path))
        
        file_path, exported_cells = _get_py_cells(py_path)
        if file_path is not None:
            notebook = Notebook(file_path)
            _overwrite_exported_cells(notebook, exported_cells)
            _save_notebook(file_path, notebook)
            print("Updated notebook: {}".format(file_path))


#%% Cell: 22
if __name__ == "__main__":
    if "--nb2all" in sys.argv:
        notebook2all()
    if "--nb2py" in sys.argv:
        notebook2py()
    if "--nb2doc" in sys.argv:
        notebook2doc()
    if "--py2nb" in sys.argv:
        python2nb()
