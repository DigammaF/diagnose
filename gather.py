
# I keep that only for the interesting way I parsed it

from typing import Any, Iterable
from json import dump

TRACERT = "tracert.txt"
PING = "ping.txt"

class Frame:

	def __init__(self, time: float, text: str):

		self.time = time
		self.text = text

	def to_dict(self) -> dict:
		return {"time": self.time, "text": self.text}

class CollectCommands:

	def __init__(self, stack: list[Collecter], frames: list[Frame]):

		self._stack = stack
		self._frames = frames
		self._commands = []

	def commit(self):

		while self._commands:
			self._commands.pop(0)()

	def _push(self, obj: Collecter):
		self._stack.append(obj)

	def push(self, obj: Collecter):
		self._commands.append(lambda self=self, obj=obj: self._push(obj))

	def _pop(self):
		self._stack.pop()

	def pop(self):
		self._commands.append(lambda self=self: self._pop())

	def insert_frame(self, frame: Frame):
		self._frames.append(frame)

	@property
	def stack_size(self) -> int:
		return len(self._stack)

class Collecter:

	def collect(line: str, commands: CollectCommands, context: dict[str, Any]): ...

class TimeCollecter(Collecter):

	def collect(line: str, commands: CollectCommands, context: dict[str, Any]):

		meta, time_text = *line.split(" ")
		assert meta == "TIME:"
		context["time"] = float(time_text)
		commands.pop()

class TextCollecter(Collecter):

	def __init__(self, delimiter: str):

		self._text: list[str] = []
		self._delimiter = delimiter.strip()

	def collect(line: str, commands: CollectCommands, context: dict[str, Any]):

		if line == self._delimiter:
			context["text"] = "\n".join(self._text)
			commands.pop()

		else:
			self._text.append(line)

class SequenceCollecter(Collecter):

	def __init__(self, collecters: list[Collecter]):

		self._collecters = collecters[:]

	def collect(line: str, commands: CollectCommands, context: dict[str, Any]):

		if self._collecters:
			commands.push(self._collecters.pop(0))

		else:
			commands.pop()

class FrameCollecter(Collecter):

	def __init__(self):

		self._blank = True

	def collect(line: str, commands: CollectCommands, context: dict[str, Any]):

		if self._blank:
			self._blank = False
			commands.push(SequenceCollecter([TimeCollecter(), TextCollecter("/>end command")]))

		else:
			commands.insert_frame(Frame(time=context["time"], text=context["text"]))

def collect(text: Iterable) -> list[Frame]:

	context: dict[str, Any] = {}
	stack: list[Collecter] = []
	frames: list[Frame] = []
	commands = CollectCommands(stack, frames)

	for line in text:

		if not stack:
			stack.append(FrameCollecter())

		line = line.strip()
		stack[-1].collect(line, commands, context)
		commands.commit()

	return frames

def collect_file(filename: str) -> list[Frame]:

	with open(filename, "r", encoding="utf-8") as f:
		return collect(f.readlines())

def dump_frames(filename: str, frames: list[Frame]):

	with open(filename, "w", encoding="utf-8") as f:
		dump([frame.to_dict() for frame in frames], f, indent=4)

def main():
	
	ping_frames = collect_file(PING)
	dump_frames("ping.json", ping_frames)
	tracert_frames = collect_file(TRACERT)
	dump_frames("tracert.json", tracert_frames)

if __name__ == "__main__":
	main()
