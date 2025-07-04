import glob, os, shutil, subprocess
import folders

def main():
    with open("firmware_strings.txt", "wb") as f:
        for name, dec in folders.vs0_decs:
            for file in glob.glob(dec+"**/*", recursive=True):
                if os.path.isdir(file):
                    continue
                out = subprocess.check_output(["strings", file])
                f.write(out)

    for name, vs0 in folders.vs0_folders:
        for rcd_file in glob.glob(vs0+"**/*.rcd", recursive=True):
            rcd_name = os.path.basename(rcd_file)
            out_file = f"firmware_rcds/{name}/{rcd_name}"
            if os.path.exists(out_file):
                print("skip", out_file)
                continue
            os.makedirs(os.path.dirname(out_file), exist_ok=True)
            shutil.copyfile(rcd_file, out_file)

main()
