import hashlib, json, os, string, glob, shutil
from xml.etree import ElementTree as ET
from io import StringIO

from util import is_hex, rcd_entry, name2id

def load_hashes_json(file: str) -> dict:
    " loads hashes from a json file "
    with open(file, "r", encoding="utf8") as f:
        names = json.load(f)
    if isinstance(names, dict):
        return {v[0:8]: k for k,v in names.items() if len(k) > 0}
    elif isinstance(names, list):
        return {name2id(v): v for v in names}

def load_hashes_txt(file: str) -> dict:
    " loads hashes from a strings file "
    with open(file, "r", encoding="utf8") as f:
        return {name2id(v): v for v in f.read().splitlines()}

def load_hashes_rcd(filename: str) -> dict:
    " loads hash dict from rcd "
    with open(filename, "r", encoding="utf8") as f:
        return {
            item["key"].lower(): item["id"]
            for item in [
                {
                    item[0]: item[1].split("(")[0].split(",")[0]
                    for item in [
                        a.split(":")
                        for a in line.split(" ")
                    ]
                }
                for line in f.read().splitlines()
                if len(line) > 0 and not line[0] == "#"
            ]
        }

def load_hashes_xml(filename: str) -> dict:
    ret = {}
    with open(filename, "r", encoding="utf8", errors="ignore") as f:
        data = f.read()
    parts2 = data.split("<?xml")
    for doc in parts2:
        doc = "".join([c for c in doc if c in string.printable])
        if len(doc) == 0:
            continue
        x = ET.parse(StringIO("<?xml"+doc))
        for elem in x.findall(".//*[@id]"):
            name = elem.get("id")
            ret[name2id(name)] = name
    return ret

def load_all_hashes():
    ids = {}
    for sony_rcd in os.listdir("sony_rcds"):
        ids.update(load_hashes_rcd("sony_rcds/"+sony_rcd))
    for string_file in os.listdir("strings"):
        ids.update(load_hashes_txt("strings/"+string_file))
    for xml_file in os.listdir("xml_with_ids"):
        ids.update(load_hashes_xml("xml_with_ids/"+xml_file))
    ids.update(load_hashes_txt("firmware_strings.txt"))
    for fw_rcd in glob.glob("firmware_rcds/**/*.rcd"):
        ids.update(load_hashes_rcd(fw_rcd))
    return ids

all_seen = set()
all_matched = set()

def generate_rcd(rco: str, hashes: dict[str, str]):
    name = os.path.splitext(os.path.basename(rco))[0]
    print(name)
    seen = set()
    matched = set()
    x = ET.parse(rco)
    with open(f"generated_rcds/{name}.rcd", "w", encoding="utf8") as f:
        f.write("#\n#\n")
        f.write(f"#               {name} - resource debug symbol file\n#\n#\n\n")

        resource = x.getroot()
        if rid := resource.get("id"):
            if name := hashes.get(rid):
                f.write("# <resource>\n")
                f.write(rcd_entry(rid, name))

        for table in resource.findall("./*"):
            f.write(f"\n# <{table.tag}>\n")
            for elem in table.findall(".//*"):
                for attrib in elem.keys():
                    val = elem.get(attrib).split("x")[-1].split(".")[0]
                    if len(val) == 8 and is_hex(val) and val not in seen:
                        if name := hashes.get(val):
                            f.write(rcd_entry(val, name))
                            matched.add(val)
                            all_matched.add(val)
                        seen.add(val)
                        all_seen.add(val)
        if len(seen):
            print(f"{len(matched)/len(seen)*100:.2f}%")
            print()

def main():
    hashes = load_all_hashes()
    os.makedirs("generated_rcds", exist_ok=True)
    for xml in glob.glob("dec_no_names/**/*.xml"):
        generate_rcd(xml, hashes)
    
    print("total:")
    print(f"{len(all_matched)/len(all_seen)*100:.2f}%")
    print(f"{len(all_matched)} of {len(all_seen)}")

    with open("generated_rcds/all.rcd", "w", encoding="utf8") as f:
        for id in sorted(all_seen, key=lambda k: ((0 if hashes.get(k) else 1), k)):
            name = hashes.get(id)
            if name is None:
                f.write("# ")
            f.write(rcd_entry(id, hashes.get(id)))
    shutil.copyfile("generated_rcds/all.rcd", "all.rcd")


main()
