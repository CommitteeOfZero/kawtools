from io import StringIO
import json
import sys
from typing import Any, TextIO

from ass_parser import (
	read_ass as parse_ass,
	AssFile,
	AssEvent,
)
from ass_tag_parser import (
	parse_ass as parse_ass_markup,
	AssText,
	AssTagAlignment,
	AssTagPosition,
)

def format_nut(value: Any) -> str:
	buffer = StringIO()

	def format_nut_string(value: str) -> None:
		buffer.write("\"")
		for char in value:
			if char == "\\":
				buffer.write("\\\\")
			if char == "\"":
				buffer.write("\\\"")
			elif char == "\n":
				buffer.write("\\\n")
			else:
				buffer.write(char)
		buffer.write("\"")

	def format_nut_value(value: Any, indent: str) -> None:
		subindent = indent + "    "
		if isinstance(value, bool):
			buffer.write("true" if value else "false")
		elif isinstance(value, (int, float)):
			buffer.write(str(value))
		elif isinstance(value, str):
			format_nut_string(value)
		elif isinstance(value, list):
			buffer.write("[\n")
			for subvalue in value:
				buffer.write(subindent)
				format_nut_value(subvalue, subindent)
				buffer.write(",\n")
			buffer.write(indent)
			buffer.write("]")
		elif isinstance(value, dict):
			buffer.write("{\n")
			for key, subvalue in value.items():
				if not isinstance(key, str):
					raise NotImplementedError(type(key).__name__)
				buffer.write(subindent)
				buffer.write(key)
				buffer.write(" = ")
				format_nut_value(subvalue, subindent)
				buffer.write(",\n")
			buffer.write(indent)
			buffer.write("}")
		else:
			raise NotImplementedError(type(value).__name__)

	format_nut_value(value, "")
	return buffer.getvalue()

def convert_ass(ass: AssFile) -> Any:
	styles = {}
	for style in ass.styles:
		styles[style.name] = style

	def convert_alignment(alignment: int) -> (int, int):
		h_align = -1 + (alignment - 1) % 3
		v_align =  1 - (alignment - 1) // 3
		return h_align, v_align

	def convert_event(event: AssEvent) -> dict:
		start = event.start * 60 // 1000
		end = event.end * 60 // 1000
		style = styles[event.style_name]

		alignment = None
		position = None
		text = ""
		for element in parse_ass_markup(event.text):
			if isinstance(element, AssText):
				text += element.text
			elif isinstance(element, AssTagAlignment):
				if alignment is None:
					alignment = element.alignment
			elif isinstance(element, AssTagPosition):
				if position is None:
					position = element.x, element.y

		if alignment is None:
			alignment = style.alignment
		h_align, v_align = convert_alignment(alignment)

		if position is None:
			absolute = False
			if h_align == -1:
				x =  style.margin_left
			elif h_align == 1:
				x = -style.margin_right
			else:
				x = 0
			if v_align == -1:
				y =  style.margin_vertical
			elif v_align == 1:
				y = -style.margin_vertical
			else:
				y = 0
		else:
			absolute = True
			x, y = position

		return {
			"start": start,
			"end": end,
			"hAlign": h_align,
			"vAlign": v_align,
			"absolute": absolute,
			"x": x,
			"y": y,
			"text": text,
		}

	events = []
	for event in ass.events:
		events.append(convert_event(event))
	return {
		"events": events,
	}

src_path = sys.argv[1]
with open(src_path, encoding="utf-8-sig") as f:
	ass = parse_ass(f)
data = convert_ass(ass)

#print(json.dumps(data, ensure_ascii=False, indent="    "), end="")
print(format_nut(data))

