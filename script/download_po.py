from pathlib import Path
import json
from babel.core import Locale
from poeditor import POEditorAPI

path_cwd = Path.cwd()

with path_cwd.joinpath("script/poediter.json").open("r") as fp:
    args = json.load(fp)

poe = POEditorAPI(args["api_token"])
domain = "py_sms_impl"

for code in map(lambda d: d["code"], poe.list_project_languages(args["id"])):
    loc_ins = Locale.parse(code, sep="-")
    dist_path = path_cwd / "locale" / str(loc_ins) / "LC_MESSAGES/py_sms_impl.po"
    poe.export(args["id"], code, local_file=str(dist_path))
    print("Downloaded: %s" % dist_path)
