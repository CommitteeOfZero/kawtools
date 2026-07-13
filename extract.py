import glob
import json
import os
import sys

def save_strings(path: str, strings: list[str]) -> None:
	with open(path, "w", encoding="utf-8") as f:
		for index, string in enumerate(strings):
			if string == "":
				raise Exception("encountered an empty string")
			f.write(f"{string}\n")

scenario_root, lines_root = sys.argv[1:]

for scenario_name in glob.glob("*.json", root_dir=scenario_root, recursive=True):
	lines_name = scenario_name.split(".")[0] + ".txt"
	scenario_path = os.path.join(scenario_root, scenario_name)
	with open(scenario_path, "r", encoding="utf-8-sig") as f:
		data = json.load(f)
	if "scenes" not in data:
		continue
	lines = []
	for scene_data in data["scenes"]:
		if "texts" not in scene_data:
			continue
		version = scene_data.get("version", 0)
		if version == 0:
			for text_data in scene_data["texts"]:
				if len(text_data) < 3:
					continue
				speaker = text_data[0]
				line_data = text_data[2]
				if isinstance(line_data, list):
					line_languages = []
					for x in line_data:
						line = x[1]
						if isinstance(speaker, str) and speaker != "":
							line = f"【{speaker}】{line}"
						line_languages.append(line)
				else:
					line = line_data
					if isinstance(speaker, str) and speaker != "":
						line = f"【{speaker}】{line}"
					line_languages = [line]
				lines.append(line_languages)
		elif version == 1:
			for text_data in scene_data["texts"]:
				if len(text_data) < 2:
					continue
				speaker = text_data[0]
				line_data = text_data[1]
				line_languages = []
				for x in line_data:
					line = x[1]
					if isinstance(speaker, str) and speaker != "":
						line = f"【{speaker}】{line}"
					line_languages.append(line)
				lines.append(line_languages)
		else:
			raise NotImplementedError(f"unrecognized version: {version}")
	if len(lines) == 0:
		continue
	language_count = len(lines[0])
	for language_index in range(language_count):
		lines_dir = os.path.join(lines_root, f"lang{language_index}")
		lines_path = os.path.join(lines_dir, lines_name)
		language_lines = []
		for line_languages in lines:
			line = line_languages[language_index]
			line = line.replace("\n", "\\n")
			language_lines.append(line)
		os.makedirs(os.path.dirname(lines_path), exist_ok=True)
		try:
			save_strings(lines_path, language_lines)
		except Exception as e:
			raise Exception(f"failed to save {lines_path}: {e}")
