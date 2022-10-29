
from time import time, sleep
from subprocess import run
from json import dump

def main():

	frames: list[dict] = []

	try:
		while True:
			sleep(0.5)
			print("BEGIN FRAME")
			now = time()
			print(f"TIME: {now}")
			print("/>begin command")
			res = run(["ping", "google.com", "-c", "1"], capture_output=True, encoding="utf-8")
			print(res.stdout)
			print("/>end command")
			print("END FRAME")

			frames.append(
				{
					"time": now,
					"text": res.stdout,
				}
			)

	except KeyboardInterrupt:
		with open("ping.json", "w", encoding="utf-8") as f:
			dump(frames, f, indent=4)

main()
