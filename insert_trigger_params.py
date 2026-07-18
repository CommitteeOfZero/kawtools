import json
import sys

def update_json(path: str, new_data) -> None:
	try:
		with open(path, "r", encoding="utf-8-sig") as f:
			old_data = json.load(f)
		if old_data == new_data:
			return
	except Exception:
		pass
	with open(path, "w", encoding="utf-8") as f:
		json.dump(new_data, f, ensure_ascii=False, indent="  ")
		f.write("\n")

lines_path, trigger_params_path = sys.argv[1:]

with open(trigger_params_path, "r", encoding="utf-8-sig") as f:
	data = json.load(f)

with open(lines_path, "r", encoding="utf-8-sig") as f:
	captions = f.read().splitlines()

if len(captions) != len(data["caption"]):
	raise Exception(f"expected {len(data['caption'])} caption lines in {lines_path}, got {len(captions)}")

data["caption"] = captions
update_json(trigger_params_path, data)
