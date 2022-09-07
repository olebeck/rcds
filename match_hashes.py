import os, json
from xml.etree import ElementTree as ET

with open("hashes.json", "r", encoding="utf8") as f:
    names = json.load(f)
ids = {v[0:8]: k for k,v in names.items()}
#assert len(ids) == len(names)

#why does python let me do this aaaaaaaaaa
_ = [ids.update({item["key"]: item["id"] for item in [{item[0]: item[1].split("(")[0].split(",")[0] for item in [a.split(":") for a in line.split(" ")]} for line in open("sony_rcds/"+sony_rcd, "r", encoding="utf8").read().splitlines() if len(line) > 0 and not line[0] == "#"]}) for sony_rcd in os.listdir("sony_rcds")]

def match_hashes(filename: str):
    " creates an rcd by matching the ids in the rco with names from hashes json "
    name = os.path.splitext(os.path.basename(filename))[0]
    print(name)
    matched = []
    x = ET.parse(filename)
    with open(f"rcds/{name}.rcd", "w", encoding="utf8") as f:
        f.write("#\n#\n")
        f.write(f"#               {name} - resource debug symbol file\n#\n#\n\n")

        for elem in x.findall(".//*[@id]"):
            elem_id = elem.get("id")
            value = ids.get(elem_id)
            if value and elem_id not in matched:
                f.write(f"key:{elem_id}(0) id:{value}\n")
                matched.append(elem_id)
    print()

def main():
    "main"
    os.makedirs("rcds", exist_ok=True)

    # awful
    for name in os.listdir("decompiled"):
        if name.endswith("_files"):
            continue
        match_hashes("decompiled/"+name)

if __name__ == "__main__":
    main()
