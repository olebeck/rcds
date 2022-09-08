import os, json
from xml.etree import ElementTree as ET

with open("hashes.json", "r", encoding="utf8") as f:
    names = json.load(f)
ids = {v[0:8]: k for k,v in names.items() if len(k) > 0}
#assert len(ids) == len(names)

#why does python let me do this aaaaaaaaaa
_ = [ids.update({item["key"]: item["id"] for item in [{item[0]: item[1].split("(")[0].split(",")[0] for item in [a.split(":") for a in line.split(" ")]} for line in open("sony_rcds/"+sony_rcd, "r", encoding="utf8").read().splitlines() if len(line) > 0 and not line[0] == "#"]}) for sony_rcd in os.listdir("sony_rcds")]

def rcd_entry(key, id):
    return f"key:{key}(0) id:{id}\n"

def match_hashes(filename: str):
    " creates an rcd by matching the ids in the rco with names from hashes json "
    name = os.path.splitext(os.path.basename(filename))[0]
    print(name)
    matched = []
    x = ET.parse(filename)
    with open(f"rcds/{name}.rcd", "w", encoding="utf8") as f:
        f.write("#\n#\n")
        f.write(f"#               {name} - resource debug symbol file\n#\n#\n\n")

        resource = x.getroot()
        if rid := resource.get("id"):
            if name := ids.get(rid):
                f.write("# <resource>")
                f.write(rcd_entry(rid, name))

        for table in resource.findall("./*"):
            f.write(f"\n# <{table.tag}>\n")
            for elem in table.findall(".//*"):
                for attrib in elem.keys():
                    val = elem.get(attrib)
                    if len(val) == 8 and all([v in "0123456789abcdef" for v in val]) and val not in matched:
                        if name := ids.get(val):
                            f.write(rcd_entry(val, name))
                            matched.append(val)
    print()

def main():
    "main"
    os.makedirs("rcds", exist_ok=True)

    for name in os.listdir("decompiled"):
        if name.endswith("_files"):
            continue
        match_hashes("decompiled/"+name)

if __name__ == "__main__":
    main()
