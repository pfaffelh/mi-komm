import pandas as pd
import jinja2
import os
import json

data = {}

data["abbrev"] = json.load(open('abbrev.json'))
data["modul"] = json.load(open('modul.json'))["modul"]
data["anforderung"] = json.load(open('anforderung.json'))["anforderung"]
data["veranstaltung"] = json.load(open('veranstaltung.json'))["veranstaltung"]

#for key, value in data["abbrev"].items():
#    print(f"{key} {value}") 


latex_jinja_env = jinja2.Environment(
    block_start_string = '\BLOCK{',
    block_end_string = '}',
    variable_start_string = '\VAR{',
    variable_end_string = '}',
    comment_start_string = '\#{',
    comment_end_string = '}',
    line_statement_prefix = '%%',
    line_comment_prefix = '%#',
    trim_blocks = True,
    autoescape = False,
    loader = jinja2.FileSystemLoader(os.path.abspath('.'))
)

template = latex_jinja_env.get_template(f"template.tex")
document = template.render(data = data)
with open(f"veranstaltung.tex",'w') as output:
    output.write(document)

