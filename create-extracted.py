import subprocess, glob, os

WITH_RCD = False
rco_path = "T:/firmware/vita/decrypted/external/official/3.60/fs/**/*.rc*"

def get_rcos():
    " list of all rcos "
    names = glob.glob(rco_path, recursive=True)
    names = [name.replace("\\","/") for name in names]
    return {
        name.split("/")[-1].split(".")[0]: name for name in names
    }

def main():
    " main "
    all_rcos = get_rcos()

    os.makedirs("decompiled", exist_ok=True)
    for k,v in all_rcos.items():
        name = k.split(".")[0]
        args = ["./CXMLDecompiler.exe", "-i", v, "-o", f"decompiled/{k}", "-d"]
        if WITH_RCD:
            args += ["-s", f"rcds/{name}.rcd"]
        proc = subprocess.run(args, check=True)
        proc.check_returncode()


if __name__ == "__main__":
    main()
