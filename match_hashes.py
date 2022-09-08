import hashlib
import os, json
from xml.etree import ElementTree as ET


def name2id(name: str) -> str:
    " converts a name into its id "
    return hashlib.sha1(name.encode("utf8")).hexdigest()[0:8]


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

#why does python let me do this aaaaaaaaaa
def load_hashes_rcd(filename: str) -> dict:
    " loads hash dict from rcd "
    with open(filename, "r", encoding="utf8") as f:
        return {
            item["key"]: item["id"]
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


def rcd_entry(key, id):
    return f"key:{key}(0) id:{id}\n"


all_seen = set()
all_matched = set()


def is_hex(val: str) -> bool:
    " checks if a string is hex "
    return all([v in "0123456789abcdef" for v in val])


def match_hashes(filename: str, ids: dict[str,str]):
    " creates an rcd by matching the ids in the rco with names from hashes json "
    name = os.path.splitext(os.path.basename(filename))[0]
    print(name)
    seen = set()
    matched = set()
    x = ET.parse(filename)
    with open(f"rcds/{name}.rcd", "w", encoding="utf8") as f:
        f.write("#\n#\n")
        f.write(f"#               {name} - resource debug symbol file\n#\n#\n\n")

        resource = x.getroot()
        if rid := resource.get("id"):
            if name := ids.get(rid):
                f.write("# <resource>\n")
                f.write(rcd_entry(rid, name))

        for table in resource.findall("./*"):
            f.write(f"\n# <{table.tag}>\n")
            for elem in table.findall(".//*"):
                for attrib in elem.keys():
                    val = elem.get(attrib)
                    if len(val) == 8 and is_hex(val) and val not in seen:
                        if name := ids.get(val):
                            f.write(rcd_entry(val, name))
                            matched.add(val)
                            all_matched.add(val)
                        seen.add(val)
                        all_seen.add(val)

        if len(seen):
            print(f"{len(matched)/len(seen)*100:.2f}%")
            print()


def load_all_hashes():
    " returns all hashes "
    ids = load_hashes_json("hashes.json")
    for sony_rcd in os.listdir("sony_rcds"):
        ids.update(load_hashes_rcd("sony_rcds/"+sony_rcd))
    ids.update(load_hashes_txt("devkit-strings.txt"))
    return ids


def main():
    "main"

    ids = load_all_hashes()
    os.makedirs("rcds", exist_ok=True)

    for name in os.listdir("decompiled"):
        if name.endswith("_files"):
            continue
        match_hashes("decompiled/"+name, ids)

    print("total:")
    print(f"{len(all_matched)/len(all_seen)*100:.2f}%")
    print(f"{len(all_matched)} of {len(all_seen)}")

    with open("rcds/all.rcd", "w", encoding="utf8") as f:
        for id in sorted(all_seen, key=lambda k: ((0 if ids.get(k) else 1), k)):
            name = ids.get(id)
            if name is None:
                f.write("# ")
            f.write(rcd_entry(id, ids.get(id)))


if __name__ == "__main__":
    main()
