# AUTOGENERATED FROM: jlabdev/convert.ipynb

#%% Cell: 0
"""doc
# 01. Convert Notebooks to *.py and *.md

> This tool allows conversion from an ipynb notebook into .py or .md files.
"""

#%% Cell: 1
from typing import List, Dict, Optional
import json
import os
import sys
import hashlib
import shutil
import base64


#%% Cell: 2
def _get_files(folder: str = ".") -> List[str]:
    file_paths = []
    for root, dirs, files in os.walk(folder):
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


#%% Cell: 3
def _join_path_cleanly(root, fname):
    joined_path = os.path.join(root, fname)
    linux_style_path = joined_path.replace("\\", "/")
    root_free_path = linux_style_path.replace("./", "")
    return root_free_path


#%% Cell: 4
def _is_notebook(file_name):
    return file_name.endswith(".ipynb")


#%% Cell: 5
def _get_notebooks(folder: str = ".") -> List[str]:
    files = _get_files(folder)
    notebooks =  filter(_is_notebook, files)
    return list(notebooks)


#%% Cell: 6
def _get_python_files(folder: str = ".") -> List[str]:
    pys = []
    for root, dirs, files in os.walk(folder):
        if ".ipynb_checkpoints" in root:
            continue
        for fname in files:
            if fname.endswith(".py"):
                pys.append(os.path.join(root, fname).replace("\\", "/").replace("./", ""))
    return pys


#%% Cell: 7
def _get_non_notebook_py_files(folder: str=".") -> List[str]:
    py_only_files = []
    py_files = _get_python_files(folder)
    notebooks = _get_notebooks(folder)
    for py_file in py_files:
        if py_file.replace(".py", ".ipynb") not in notebooks:
            py_only_files.append(py_file)
    return py_only_files


#%% Cell: 8
def _get_notebook(file_path: str) -> Dict:
    with open(file_path, "r", encoding="utf8") as f:
        return json.loads(f.read())


#%% Cell: 9
def _is_non_empty_code_cell(cell):
    return cell["cell_type"] == "code" and len(cell["source"]) > 0


#%% Cell: 10
def _is_non_empty_markdown_cell(cell):
    return cell["cell_type"] == "markdown" and len(cell["source"]) > 0


#%% Cell: 11
def _is_convertible_nb(data, find_examples=False) -> bool:
    for cell in data["cells"]:
        if not _is_non_empty_code_cell(cell):
            continue
        if cell["source"][0].startswith("#convert"):
            return True
        if find_examples and cell["source"][0].startswith("#example"):
            return True
    return False


#%% Cell: 12
def _is_exportable_cell(cell) -> bool:
    exportable = _is_non_empty_code_cell(cell) and cell["source"][0].startswith("#export")
    exportable |= _is_non_empty_markdown_cell(cell) and not cell["source"][0].startswith("#hide") and not cell["source"][0].startswith("<!-- hide -->")
    return exportable


#%% Cell: 13
def _get_exportable_cells(data):
    return list(filter(_is_exportable_cell, data["cells"]))


#%% Cell: 14
def _update_cell_header(cell, cell_idx):
    cell["source"][0] = cell["source"][0].replace("#export", "#%% Cell: {}".format(cell_idx))


#%% Cell: 15
def _combine_cells_to_code(cells, file_path: str) -> str:
    code = "# AUTOGENERATED FROM: {}\n\n".format(file_path)
    for cell_idx, cell in enumerate(cells):
        _update_cell_header(cell, cell_idx)
        # Add cell source to code
        if _is_non_empty_markdown_cell(cell):
            code += "#%% Cell: {}\n".format(cell_idx)
            code += "\"\"\"doc\n"
        code += "".join(cell["source"])
        if _is_non_empty_markdown_cell(cell):
            while code.endswith("\n"):
                code = code[:-2]
            code += "\n\"\"\"\n"
        # Ensure there are two empty lines between cells
        code += "\n\n\n"
        while code.endswith("\n\n\n\n"):
            code = code[:-2]
    
    # Ensure there is a single new line at file end.
    while code.endswith("\n\n"):
        code = code[:-2]
    return code


#%% Cell: 16
def _get_py_paths(file_path: str, root: str="."):
    py_package = file_path.replace("/", ".").replace("..", ".").replace(".ipynb", "")
    py_path = os.path.join(root, py_package.replace(".", os.sep) + ".py")
    package_path = os.path.join(root, os.sep.join(py_package.split(".")[:-1]))
    return py_path, package_path


#%% Cell: 17
def _write_py(code, file_path: str, root: str= ".") -> None:
    py_path, package_path = _get_py_paths(file_path, root)
    os.makedirs(package_path, exist_ok=True)
    with open(py_path, "w", encoding="utf8") as f:
        f.write(code)


#%% Cell: 18
"""doc
## Convert all Notebooks in a Folder to Python

One core feature of this library is to convert all notebook files located beneath the `nb_root` folder into python files relative to the `project_root`.
For this conversion the notebook is scanned for:

1. A code cell which contians `#default_exp python_package.for.this.notebook`
2. All code cells where the first line is `#export`

Then using the cells marked with `#export` a python file in `python_package/for/this/notebook.py` is created.
The generated python file should not be modified and the cell and AUTOGENERATED comments must not be deleted.
"""

#%% Cell: 19
def notebook2py(project_root: str = ".") -> None:
    """Convert all notebooks in the folder.
    
    :param project_root: The root directory of the project. The default exp path is relative to this folder.
    :type project_root: str, optional
    """
    notebooks = _get_notebooks(project_root)
    for file_path in notebooks:
        print("Converting to py: {}".format(file_path))
        notebook = _get_notebook(file_path)
        if _is_convertible_nb(notebook): 
            exportable_cells = _get_exportable_cells(notebook)
            code = _combine_cells_to_code(exportable_cells, file_path)
            _write_py(code, file_path, root=project_root)


#%% Cell: 20
def _extract_doc(source:str, source_path_relative:str = None) -> str:
    lines = source.split("\n")
    docs = []
    mode = 0
    in_multiline_string = False
    current_doc = []
    current_doc_indentation = 0
    args = ""
    for line_idx, orig_line in enumerate(lines):
        line = orig_line.lstrip()
        if "\"\"\"" in line:
            in_multiline_string = not in_multiline_string
        indent = len(orig_line) - len(line)
        if mode == 0 or mode == 1:
            if (line.startswith("def ") or line.startswith("class ")) and not (line.startswith("def _") or line.startswith("class _")):
                if mode == 1:
                    docs.append(current_doc)
                level = int(indent / 4) + 1
                if line.startswith("class "):
                    # Handle class headers
                    superclass = ""
                    if "(" in line:
                        fun_name, superclass = line.split(" ")[1].split("(")
                        superclass = "(" + superclass.split(")")[0] + ")"
                    else:
                        fun_name = line.split(" ")[1].split(":")[0]
                    current_doc = ["---\n#" + ("#"*level) + " *class* **" + fun_name + "**" + superclass, ""]
                else:
                    # Handle function headers
                    fun_name, args = line.split(" ")[1].split("(")
                    current_doc = ["---\n#" + ("#"*level) + " *def* **" + fun_name + "**", ""]
                if source_path_relative is not None:
                    # Add line info for python file.
                    current_doc[0] += f" [[src]]({source_path_relative}#L{line_idx+1})"
                mode = 1
            elif mode == 0 and line.startswith("\"\"\"doc") and in_multiline_string:
                # Start module docstring """doc
                current_doc_indentation = indent
                mode = 2
                current_doc = ["---\n", ""]
            elif mode == 1 and line.startswith("\"\"\"") and in_multiline_string:
                # Start docstring for function/class """
                current_doc_indentation = indent
                line = line[3:]
                mode = 2
                if line.rstrip().endswith("\"\"\""):
                    # if directly ends again, directly add and close
                    current_doc[1] += line[:-3].lstrip().rstrip() + "\n"
                    mode = 0
                    docs.append(current_doc)
                    current_doc = []
                else:
                    if len(line.lstrip().rstrip()) > 0:
                        current_doc[1] += line.lstrip().rstrip() + "\n"
        elif mode == 2:
            # Currently reading a docstring
            if "\"\"\"" in line:
                # Close the open doc """
                mode = 0
                docs.append(current_doc)
                current_doc = []
            else:
                # Append a line to the documentation.
                current_doc[1] += orig_line[current_doc_indentation:].rstrip() + "\n"

    if len(current_doc) > 0:
        docs.append(current_doc)

    if len(docs) == 0:
        return ""
    
    output = ""
    for doc in docs:
        output += doc[0] + "\n\n"
        if doc[1] == "":
            doc[1] = "*(no documentation found)*"

        lines = doc[1].split("\n")
        out_lines = []
        for line in lines:
            if line.lstrip().startswith(":param"):
                line = line.replace(":param ", "* **")
                end_of_param = line.index(":")
                line = line[:end_of_param] + "**" + line[end_of_param:]
            # If there is a type parameter amend the last param line and add types.
            if line.lstrip().startswith(":type"):
                line = line.replace(":type ", "")
                end_of_param = line.index(":")
                param_name = line[:end_of_param]
                param_type = line[(end_of_param+1):].lstrip().rstrip()
                old_param_header = f"* **{param_name}**:"
                if out_lines[-1].startswith(old_param_header):
                    new_param_header = f"* **{param_name}** *({param_type})*:"
                    out_lines[-1] = out_lines[-1].replace(old_param_header, new_param_header)
                    continue
                else:
                    print("ERROR: Invalid doc format, ':param X:' must come before ':type X:'.")
            # :return: is an easy replace.
            line = line.replace(":return:", "* **returns**:")
            # If there is a return type amend the last line and add types.
            if line.lstrip().startswith(":rtype:"):
                line = line.replace(":rtype:", "").lstrip().rstrip()
                old_param_header = f"* **returns**:"
                if out_lines[-1].startswith(old_param_header):
                    new_param_header = f"* **returns** *({line})*:"
                    out_lines[-1] = out_lines[-1].replace(old_param_header, new_param_header)
                    continue
                else:
                    print("ERROR: Invalid doc format, ':return:' must come before ':rtype:'.")
            out_lines.append(line)
        doc[1] = "\n".join(out_lines)
        output += doc[1]
        output += "\n\n"
        
    return output


#%% Cell: 21
def _fix_paths(doc: str) -> str:
    start = 0
    idx = doc.find("![", start)
    while idx >= 0:
        left = doc.find("](", idx)
        if left != doc.find("](data:", idx):
            doc = doc[:left] + "](../" + doc[left+2:]
        start = idx + 1
        idx = doc.find("![", start)
    return doc


#%% Cell: 22
def _get_doc(data, base_path_relative, root_path) -> str:
    doc = "[Back to Overview]({})\n\n".format(base_path_relative + "/README.md")
    images = {}
    title = None
    for cell in data["cells"]:
        # Example Cell
        if cell["cell_type"] == "code" and len(cell["source"]) > 0 and not cell["source"][0].startswith("#export") and not cell["source"][0].startswith("#hide") and not cell["source"][0].startswith("#convert") and not cell["source"][0].startswith("#example"):
            doc += "Example:\n"
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
                doc += "Output:\n"
                doc += "```\n"
                doc += outp_text
                doc += "\n```\n"
            for img in image_data:
                md5 = hashlib.md5(img.encode('utf-8')).hexdigest()
                with open(root_path + "/docs/jlabdev_images/{}.png".format(md5), "wb") as fh:
                    
                    fh.write(base64.b64decode(img))
                doc +="![data](" + base_path_relative + "/docs/jlabdev_images/{}.png)\n".format(md5)
            doc += "\n"

        # Export Cell
        if cell["cell_type"] == "code" and len(cell["source"]) > 0 and cell["source"][0].startswith("#export"):
            source = "".join(cell["source"])
            doc += _extract_doc(source)
            
        # Regular Markdown Cell
        if cell["cell_type"] == "markdown" and len(cell["source"]) > 0 and not cell["source"][0].startswith("#hide"):
            for line in cell["source"]:
                if line.startswith("# ") and title is None:
                    title = line[2:]
                doc += line
            doc += "\n\n"

    doc = _fix_paths(doc)
    
    return doc, title


#%% Cell: 23
def _write_md(file_path, root: str = ".") -> str:
    notebook = _get_notebook(file_path)
    if not _is_convertible_nb(notebook, find_examples=True):
        return None, None
    doc_path = os.path.join(root, "docs")
    os.makedirs(doc_path, exist_ok=True)
    
    py_package = file_path.replace("/", ".").replace("..", ".").replace(".ipynb", "")
    md_name = py_package.replace(".", "/") + ".md"
    md_path = os.path.join(root, "docs", md_name).replace("\\", "/")
    base_path_relative = "/".join([".." for _ in range(len(md_name.split("/"))-1)])
    doc, title = _get_doc(notebook, base_path_relative, root)
    path = "/".join(md_path.split("/")[:-1])
    if not os.path.exists(path):
        os.makedirs(path)
    with open(md_path, "w", encoding="utf8") as f:
        f.write(doc)
    return md_name, title


#%% Cell: 24
def _get_doc_py(source, base_path_relative, root_path, source_path_relative) -> str:
    doc = "[Back to Overview]({})\n\n".format(base_path_relative + "/README.md")
    doc += _extract_doc("".join(source), source_path_relative)
    doc = _fix_paths(doc)
    return doc, source[1][2:]


#%% Cell: 25
def _write_md_py(file_path, root: str = ".") -> str:
    with open(file_path, "r") as f:
        source = f.readlines()
    if not len(source) > 2 or not source[0].startswith("\"\"\"") or not source[1].startswith("# "):
        return None, None
    doc_path = os.path.join(root, "docs")
    os.makedirs(doc_path, exist_ok=True)
    
    py_package = file_path.replace("/", ".").replace("..", ".").replace(".py", "")
    md_name = py_package.replace(".", "/") + ".md"
    md_path = os.path.join(root, "docs", md_name).replace("\\", "/")
    base_path_relative = "/".join([".." for _ in range(len(md_name.split("/"))-1)])
    source_path_relative = os.path.join("..", base_path_relative, md_name.replace(".md", ".py"))
    doc, title = _get_doc_py(source, base_path_relative, root, source_path_relative)
    path = "/".join(md_path.split("/")[:-1])
    if not os.path.exists(path):
        os.makedirs(path)
    with open(md_path, "w", encoding="utf8") as f:
        f.write(doc)
    return md_name, title


#%% Cell: 26
"""doc
## Convert all Notebooks in a Folder to Markdown

One core feature of this library is to convert all notebook files located beneath the `nb_root` folder into python files relative to the `project_root`.
For this conversion the notebook is scanned for:

1. A code cell which contians `#default_exp python_package.for.this.notebook` is searched to find the output file name.
2. All cells are scanned and based on their type an action is taken:
    * `#hide` -> Cell is ignored.
    * markdown -> The cell is 1 to 1 copied into the doc.
    * `#export` code cell -> The cell is scanned for any public function and class. They are added with their docstring to the markdown.
    * other code cell -> The cell is treated as an example and the code and the output are inserted into the markdown
"""

#%% Cell: 27
README_TEMPLATE = """
# Examples

{examples}

# Documentation

{toc}

"""


#%% Cell: 28
def notebook2doc(project_root: str = ".") -> None:
    """Convert all notebooks in the folder.

    Also converts notebooks annotated with #example in first cell.
    All notebooks, which have a title starting with "Example: " are listed under examples without the "Example: " shown in the list.
    
    :param project_root: The root directory of the project. The default exp path is relative to this folder.
    :type project_root: str, optional
    """
    readme_template = README_TEMPLATE
    notebooks = _get_notebooks(project_root)
    non_notebooks = _get_non_notebook_py_files(project_root)
    index = []
    shutil.rmtree(os.path.join(project_root, "docs"))
    os.makedirs(os.path.join(project_root, "docs", "jlabdev_images"))
    for nb_path in notebooks:
        print("Converting to md: {}".format(nb_path))
        name, title = _write_md(nb_path, root=project_root)
        if name is not None:
            index.append((name, title))
    for py_path in non_notebooks:
        print("Converting to md: {}".format(py_path))
        name, title = _write_md_py(py_path, root=project_root)
        if name is not None:
            index.append((name, title))
    
    index = sorted(index, key=lambda x: x[1])
    
    if len(index) > 0:
        with open(os.path.join(project_root, "docs", "README.md"), "w", encoding="utf8") as f:
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


#%% Cell: 29
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
        if line.startswith("# Cell:"):
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


#%% Cell: 30
def _overwrite_exported_cells(data, cells):
    i = 0
    for cell in data["cells"]:
        if _is_non_empty_code_cell(cell) and cell["source"][0].startswith("#export"):
            cell["source"] = ["#export\n"] + cells[i]
        if _is_non_empty_markdown_cell(cell) and not cell["source"][0].startswith("#hide"):
            cells[i][-2] = cells[i][-2][:-1]
            cell["source"] = cells[i][1:-1]
        if _is_exportable_cell(cell):
            i += 1


#%% Cell: 31
def _save_notebook(file_path: str, notebook: Dict) -> None:
    with open(file_path, "w", encoding="utf8") as f:
        return f.write(json.dumps(notebook, indent=1) + "\n")


#%% Cell: 32
def python2nb(project_root: str = ".") -> None:
    """
    Convert all notebooks in the folder.
    
    :param project_root: The root directory of the project. The default exp path is relative to this folder.
    :type project_root: str, optional
    """
    readme_template = README_TEMPLATE
    pyfiles = _get_python_files(project_root)
    index = []
    for py_path in pyfiles:
        print("Converting to notebook: {}".format(py_path))
        
        file_path, exported_cells = _get_py_cells(py_path)
        if file_path is not None:
            notebook = _get_notebook(file_path)
            _overwrite_exported_cells(notebook, exported_cells)
            _save_notebook(file_path, notebook)
            print("Updated notebook: {}".format(file_path))


#%% Cell: 33
def notebook2all(project_root: str = ".") -> None:
    """Run the notebook2py and notebook2doc commands.

    :param project_root: The path to the project root, defaults to ".".
    :type project_root: str, optional
    """
    notebook2py(project_root)
    notebook2doc(project_root)


#%% Cell: 34
if __name__ == "__main__":
    if "--nb2all" in sys.argv:
        notebook2all()
    if "--nb2py" in sys.argv:
        notebook2py()
    if "--nb2doc" in sys.argv:
        notebook2doc()
    if "--py2nb" in sys.argv:
        python2nb()
