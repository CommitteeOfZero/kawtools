from dataclasses import dataclass
import glob
import json
import os
import re
import sys
from typing import Optional

def load_text(path: str) -> str:
	with open(path, "r", encoding="utf-8-sig") as f:
		return f.read()

def update_json(path: str, new_data) -> None:
	try:
		with open(path, "r", encoding="utf-8-sig") as f:
			old_data = json.load(f)
		if old_data == new_data:
			return
	except Exception:
		pass
	with open(path, "w", encoding="utf-8") as f:
		json.dump(new_data, f, ensure_ascii=False, indent="  ", sort_keys=True)
		f.write("\n")

START_TAG_RE = r'<tip name="(?P<name>[^"]*)" ctgr="(?P<ctgr>[^"]*)" ruby="(?P<ruby>[^"]*)" index="(?P<index>[^"]*)">'
END_TAG = '</tip>'
NOTE_LINE_PREFIX = "\t"

@dataclass
class StartTag:
	name: str
	ctgr: str
	ruby: str
	index: int

@dataclass
class Tip:
	internal_index: int
	name: str
	ctgr: str
	ruby: str
	note: str

class TipsParser:
	def __init__(self, text: str):
		self.lines = text.splitlines()
		self.position = 0
		self.tips: list[Tip] = []

	def parse(self) -> dict:
		self.skip_blank_lines()
		while not self.is_eof():
			tag = self.parse_start_tag()
			note = self.parse_to_end_tag()
			self.tips.append(Tip(
				internal_index=tag.index,
				name=tag.name,
				ctgr=tag.ctgr,
				ruby=tag.ruby,
				note=note,
			))
			self.skip_blank_lines()

		i2d = [None]*len(self.tips)
		d2i = [None]*len(self.tips)
		tips_data = [None]*len(self.tips)
		for display_index, tip in enumerate(self.tips):
			i2d[tip.internal_index] = display_index
			d2i[display_index] = tip.internal_index
			tips_data[display_index] = {
				"name": tip.name,
				"ctgr": tip.ctgr,
				"ruby": tip.ruby,
				"note": tip.note,
			}
		return {
			"conv_d2i": d2i,
			"conv_i2d": i2d,
			"tips_list": tips_data,
		}

	def parse_start_tag(self) -> StartTag:
		line = self.next()
		match = re.fullmatch(START_TAG_RE, line)
		if match is None:
			raise Exception(f"invalid start tag: {line!r}")
		return StartTag(
			name=match.group("name"),
			ctgr=match.group("ctgr"),
			ruby=match.group("ruby"),
			index=int(match.group("index")),
		)

	def parse_to_end_tag(self) -> str:
		lines = []
		while True:
			if self.is_eof():
				raise Exception("unexpected eof")
			line = self.next()
			if line == END_TAG:
				break
			if line == "":
				lines.append("")
				continue
			if line == " ":
				lines.append(" ")
				continue
			if not line.startswith(NOTE_LINE_PREFIX):
				raise Exception(f"invalid note line: {line!r}")
			lines.append(line.removeprefix(NOTE_LINE_PREFIX))
		return "\n".join(lines)

	def skip_blank_lines(self) -> None:
		while True:
			if self.is_eof():
				break
			if self.peek() != "":
				break
			self.next()

	def peek(self) -> str:
		return self.lines[self.position]

	def next(self) -> str:
		tmp = self.lines[self.position]
		self.position += 1
		return tmp

	def is_eof(self) -> bool:
		return self.position >= len(self.lines)

def parse_tips(text: str) -> dict:
	return TipsParser(text).parse()

lines_root, tips_path = sys.argv[1:]

with open(tips_path, "r", encoding="utf-8-sig") as f:
	data = json.load(f)

languages = data["language"]
for language_index in range(len(languages)):
	lines_path = os.path.join(lines_root, f"lang{language_index}", "tips.txt")
	if not os.path.exists(lines_path):
		continue
	formatted_tips = load_text(lines_path)
	languages[language_index] = parse_tips(formatted_tips)

update_json(tips_path, data)
