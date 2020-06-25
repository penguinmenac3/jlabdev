# AUTOGENERATED FROM: jlabdev/convert.ipynb

# Cell: 0
from typing import List, Dict, Optional
import json
import os
import sys


# Cell: 1
def _get_notebooks(folder: str = ".") -> List[str]:
    nbs = []
    for root, dirs, files in os.walk(folder):
        if ".ipynb_checkpoints" in root:
            continue
        for fname in files:
            if fname.endswith(".ipynb"):
                nbs.append(os.path.join(root, fname).replace("\\", "/").replace("./", ""))
    return nbs


# Cell: 2
def _get_notebook(file_path: str) -> Dict:
    with open(file_path, "r") as f:
        return json.loads(f.read())


# Cell: 3
def _convertible_nb(data) -> str:
    for cell in data["cells"]:
        if cell["cell_type"] == "code" and len(cell["source"]) > 0 and cell["source"][0].startswith("#convert"):
            return True
    return False


# Cell: 4
def _get_exported_cells(data) -> List:
    exported_cells = []
    for cell in data["cells"]:
        if cell["cell_type"] == "code" and len(cell["source"]) > 0 and cell["source"][0].startswith("#export"):
            cell["source"][0] = cell["source"][0].replace("#export", "# Cell: {}".format(len(exported_cells)))
            exported_cells.append(cell)
    return exported_cells


# Cell: 5
def _combine_cells_to_code(cells, file_path: str) -> str:
    code = "# AUTOGENERATED FROM: {}\n\n".format(file_path)
    for cell in cells:
        for line in cell["source"]:
            code += line
        # Ensure there are two empty lines between cells
        code += "\n\n\n"
        while code.endswith("\n\n\n\n"):
            code = code[:-2]
    
    # Ensure there is a single new line at file end.
    while code.endswith("\n\n"):
        code = code[:-2]
    return code


# Cell: 6
def _write_py(notebook, file_path: str, root: str= ".") -> None:
    exported_cells = _get_exported_cells(notebook)
    if not _convertible_nb(notebook):
        return
    py_package = file_path.replace("/", ".").replace("..", ".").replace(".ipynb", "")
    py_path = os.path.join(root, py_package.replace(".", os.sep) + ".py")
    code = _combine_cells_to_code(exported_cells, file_path)
    package_path = os.path.join(root, os.sep.join(py_package.split(".")[:-1]))
    os.makedirs(package_path, exist_ok=True)
    with open(py_path, "w") as f:
        f.write(code)


# Cell: 7
def notebook2py(project_root: str = ".") -> None:
    """
    Convert all notebooks in the folder.
    
    :param project_root: The root directory of the project. The default exp path is relative to this folder.
    :param nb_root: The root directory of all the notebooks. Only notebooks in this or any subfolder will be considered.
    """
    notebooks = _get_notebooks(project_root)
    for nb_path in notebooks:
        print("Converting to py: {}".format(nb_path))
        notebook = _get_notebook(nb_path)
        _write_py(notebook, nb_path, root=project_root)


# Cell: 8
def _extract_doc(source:str) -> str:
    lines = source.split("\n")
    docs = []
    mode = 0
    for line in lines:
        if mode == 0:
            if ("def " in line or "class " in line) and not ("def _" in line or "class _" in line):
                current_doc = [line, ""]
                mode = 1
        elif mode == 1:
            if "\"\"\"" in line:
                mode = 2
            else:
                mode = 0
                docs.append(current_doc)
        elif mode == 2:
            if "\"\"\"" in line:
                mode = 0
                docs.append(current_doc)
            else:
                current_doc[1] += line.lstrip() + "\n"                
        
    if len(docs) == 0:
        return ""
    
    output = ""
    for doc in docs:
        output += "**" + doc[0] + "**\n\n"
        output += doc[1].replace(":param", "*")
        output += "\n\n"
        
    return output


# Cell: 9
def _get_doc(data) -> str:
    doc = ""
    title = None
    for cell in data["cells"]:
        # Example Cell
        if cell["cell_type"] == "code" and len(cell["source"]) > 0 and not cell["source"][0].startswith("#export") and not cell["source"][0].startswith("#hide") and not cell["source"][0].startswith("#convert"):
            doc += "Example:\n"
            doc += "```python\n"
            for line in cell["source"]:
                doc += line
            doc += "\n```\n"
            doc += "Output:\n"
            doc += "```\n"
            for outp in cell["outputs"]:
                if "text" in outp:
                    for entry in outp["text"]:
                        doc += entry
                if "traceback" in outp:
                    for entry in outp["traceback"]:
                        while entry.find('\x1b') >= 0:
                            start = entry.find('\x1b')
                            end = entry.find("m", start)
                            entry = entry[:start] + entry[end+1:]
                        doc += entry + "\n"
            doc += "\n```\n"
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
    return doc, title


# Cell: 10
def _write_md(file_path, root: str = ".") -> str:
    notebook = _get_notebook(file_path)
    doc_path = os.path.join(root, "docs")
    os.makedirs(doc_path, exist_ok=True)
    
    py_package = file_path.replace("/", ".").replace("..", ".").replace(".ipynb", "")
    md_name = py_package.replace(".", "/") + ".md"
    md_path = os.path.join(root, "docs", md_name).replace("\\", "/")
    doc, title = _get_doc(notebook)
    path = "/".join(md_path.split("/")[:-1])
    if not os.path.exists(path):
        os.makedirs(path)
    with open(md_path, "w") as f:
        f.write(doc)
    return md_name, title


# Cell: 11
README_TEMPLATE = """
# Package List

{toc}

"""


# Cell: 12
def notebook2md(project_root: str = ".") -> None:
    """
    Convert all notebooks in the folder.
    
    :param project_root: The root directory of the project. The default exp path is relative to this folder.
    :param nb_root: The root directory of all the notebooks. Only notebooks in this or any subfolder will be considered.
    """
    readme_template = README_TEMPLATE
    notebooks = _get_notebooks(project_root)
    index = []
    for nb_path in notebooks:
        print("Converting to md: {}".format(nb_path))
        index.append(_write_md(nb_path, root=project_root))
    
    index = sorted(index, key=lambda x: x[1])
    
    if len(index) > 0:
        with open(os.path.join(project_root, "docs", "README.md"), "w") as f:
            toc = ""
            for i in index:
                toc += "* [{}]({})\n".format(i[1], i[0])
            readme_template = readme_template.replace("`{toc}`", "`#toc%`").format(toc=toc).replace("`#toc%`", "`{toc}`")
            f.write(readme_template)


# Cell: 13
if __name__ == "__main__":
    if "--nb2py" in sys.argv:
        notebook2py()
    if "--nb2md" in sys.argv:
        notebook2md()