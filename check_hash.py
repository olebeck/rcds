from collections import defaultdict
from re import M
import sys, os
from xml.etree import ElementTree as ET

import util

if len(sys.argv) != 2:
    print("usage: check_hash.py <name>")


def find_matches(filename, ids) -> dict:
    " checks how many times an id is in this file "
    ret = defaultdict(int)
    seen = set()

    x = ET.parse(filename)
    resource = x.getroot()
    if rid := resource.get("id"):
        if ids.get(rid):
            ret[rid] += 1

    for table in resource.findall("./*"):
        for elem in table.findall(".//*"):
            for attrib in elem.keys():
                val = elem.get(attrib)
                if len(val) == 8 and util.is_hex(val) and val not in seen:
                    if ids.get(val):
                        ret[val] += 1
                    seen.add(val)
    return ret


def main():
    " main "
    ids = {
        match_hashes.name2id(name): name
        for name in sys.argv[1:]
    }

    print(f"{len(ids)} ids")

    for name in os.listdir("decompiled"):
        if name.endswith("_files"):
            continue
        for id, count in find_matches("decompiled/"+name, ids).items():
            print(name, id, ids.get(id), count)


if __name__ == "__main__":
    main()
