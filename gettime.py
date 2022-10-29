
from json import load, dumps
from sys import argv

TRACERT = "tracert.json"
PING = "ping.json"

def load_frames(filename: str) -> list[dict]:

	with open(filename, "r", encoding="utf-8") as f:
		return load(f.read())

def get_closest(time: float, frames: list[dict]):
	return min(frames, key = lambda e: float(e["time"] - time))

def print_frame(frame: dict):
	print(dumps(frame, indent=4))

ping_frames = load_frames(PING)
tracert_frames = load_frames(TRACERT)
target_time = float(argv[1])

print_frame(get_closest(target_time, ping_frames))
print_frame(get_closest(target_time, tracert_frames))
