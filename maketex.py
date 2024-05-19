import pandas as pd
import jinja2
import os
import json
from util.vvz import makedata
from util.config import *

data = makedata(sem_shortname)
with open(f"data/{sem_shortname}.json", "w") as fp:
    json.dump(data, fp)

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

template = latex_jinja_env.get_template(f"latex/template.tex")
document = template.render(data = data)
with open(f"latex/veranstaltungen_{sem_shortname}.tex",'w') as output:
    output.write(document)

