import glob
import json
import os
import sys

patch_dir, out_path = sys.argv[1:]

file_info = {}
for name in sorted(glob.glob("*.m", root_dir=patch_dir)):
	file_info[name] = [0, 0]

manifest = {
	"expire_suffix_list": [".psb.m"],
	"file_info": file_info,
	"info": "archive",
	"version": 1.0,
}

with open(out_path, "w", encoding="utf-8") as f:
	json.dump(manifest, f, ensure_ascii=False, indent="  ")
	f.write("\n")
