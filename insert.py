import glob
import json
import os
import re
import sys

name_re = re.compile(r"^【(.+?)】(.+)$")

def load_strings(path: str) -> list[str]:
	with open(path, "r", encoding="utf-8-sig") as f:
		lines = f.read().splitlines()
	strings = []
	for line in lines:
		if line == "":
			raise Exception("encountered an empty string")
		strings.append(line)
	return strings

def split_name(text: str):
	m = name_re.match(text)
	if m:
		return m.group(1), m.group(2)
	return None, text

class Inserter:
	def __len__(self) -> int:
		return self._length()

	def __setitem__(self, index: int, text: str) -> None:
		if index not in range(len(self)):
			raise IndexError
		self._insert(index, text)

	def _length(self) -> int:
		raise NotImplementedError

	def _insert(self, index: int, text: str) -> None:
		raise NotImplementedError

class InserterOne(Inserter):
	def __init__(self, text_data: list):
		self._text_data = text_data

	def _length(self) -> int:
		return 1

	def _insert(self, index: int, text: str) -> None:
		name, body = split_name(text)
		if name is not None:
			self._text_data[0] = name
		self._text_data[2] = body

class InserterMultiple(Inserter):
	def __init__(self, line_data: list, text_data: list | None):
		self._line_data = line_data
		self._text_data = text_data

	def _length(self) -> int:
		return len(self._line_data)

	def _insert(self, index: int, text: str) -> None:
		name, body = split_name(text)
		if name is not None and self._text_data is not None:
			self._text_data[0] = name
		self._line_data[index][1] = body

lines_root, scenario_root = sys.argv[1:]

for scenario_name in glob.glob("*.json", root_dir=scenario_root, recursive=True):
	lines_name = scenario_name.split(".")[0] + ".txt"
	scenario_path = os.path.join(scenario_root, scenario_name)
	with open(scenario_path, "r", encoding="utf-8-sig") as f:
		data = json.load(f)
	if "scenes" not in data:
		continue
	inserters = []
	for scene_data in data["scenes"]:
		if "texts" not in scene_data:
			continue
		version = scene_data.get("version", 0)
		for text_data in scene_data["texts"]:
			if version == 0:
				if len(text_data) < 3:
					continue
				line_data = text_data[2]
				if isinstance(line_data, list):
					inserter = InserterMultiple(line_data, text_data)
				else:
					inserter = InserterOne(text_data)
			elif version == 1:
				if len(text_data) < 2:
					continue
				line_data = text_data[1]
				inserter = InserterMultiple(line_data, None)
			else:
				raise NotImplementedError(f"unrecognized version: {version}")
			inserters.append(inserter)
	if len(inserters) == 0:
		continue
	language_count = len(inserters[0])
	for language_index in range(language_count):
		lines_dir = os.path.join(lines_root, f"lang{language_index}")
		lines_path = os.path.join(lines_dir, lines_name)
		try:
			language_lines = load_strings(lines_path)
		except Exception as e:
			raise Exception(f"failed to load {lines_path}: {e}")
		if len(inserters) != len(language_lines):
			raise Exception("line count mismatch")
		for line_index, inserter in enumerate(inserters):
			inserter[language_index] = language_lines[line_index]
	with open(scenario_path, "w", encoding="utf-8") as f:
		json.dump(data, f, ensure_ascii=False, indent="  ")
		f.write("\n")
