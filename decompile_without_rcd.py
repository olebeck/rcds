import subprocess, glob, os
import folders

def acdc(filename: str, output: str):
    print("acdc", filename)
    subprocess.check_call(["./acdc/build/acdc", "-d", "--cxml", filename, "--xml", output])

for name, vs0 in folders.vs0_folders:
    for rcd_file in glob.glob(vs0+"**/*.rco", recursive=True):
        rcd_name = os.path.basename(rcd_file)
        out_file = f"dec_no_names/{name}/{os.path.splitext(rcd_name)[0]}.xml"
        if os.path.exists(out_file):
            print("skip", out_file)
            continue
        os.makedirs(os.path.dirname(out_file), exist_ok=True)
        acdc(rcd_file, out_file)
