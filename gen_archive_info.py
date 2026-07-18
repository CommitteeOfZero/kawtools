import glob
import json
import os
import sys

args = sys.argv[1:]
patch_dir, out_path = args[0], args[1]
glob_pattern = args[2] if len(args) > 2 else "*.m"
expire_suffix = args[3] if len(args) > 3 else ".psb.m"

file_info = {}
for name in sorted(glob.glob(glob_pattern, root_dir=patch_dir)):
	file_info[name] = [0, 0]

manifest = {
	"expire_suffix_list": [expire_suffix],
	"file_info": file_info,
	"info": "archive",
	"version": 1.0,
}

with open(out_path, "w", encoding="utf-8") as f:
	json.dump(manifest, f, ensure_ascii=False, indent="  ")
	f.write("\n")
