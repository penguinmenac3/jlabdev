from jlabdev.nb_convert import notebook2py, notebook2md

if __name__ == "__main__":
    notebook2py(".", "notebooks")
    notebook2md(".", "notebooks")
