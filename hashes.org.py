#!/usr/bin/python3

import html
import json
import multiprocessing
import os
import requests
import tqdm


def createSession():
	headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.74 Safari/537.36 Edg/79.0.309.43",
		"Referer": "https://hashes.org/"
	}

	session = requests.Session()
	session.headers.update(headers)
	return session


def queryLeaks(session):
	response = session.get("https://hashes.org/api/data.php?select=leaks")
	leaks = json.loads(response.content.strip())
	response = session.get("https://hashes.org/api/data.php?select=lists")
	leaks += json.loads(response.content.strip())
	return leaks


def fetchLeak(session, leak):
	response = session.get("https://hashes.org/download.php?hashlistId={0}&type=found".format(leak["id"]), stream=True)

	with open("{0}.leak".format(leak["id"]), "wb") as leakFile:
		for chunk in response.iter_content(chunk_size=1024):
			if chunk:
				leakFile.write(chunk)


def sortUnique(sourceFile, targetFile):
	os.system("sort -u --parallel={0} {1} >> {2}".format(multiprocessing.cpu_count(), sourceFile, targetFile))


def diff(oldFile, newFile, outFile):
	os.system("comm -13 {0} {1} > {2}".format(oldFile, newFile, outFile))


def main():
	session = createSession()
	leaks = queryLeaks(session)
	padding = 0

	for leak in leaks:
		if int(leak["found"].replace("'", "")):
			info = "{0} [{1}]".format(html.unescape(leak["name"].split("<br><code>")[0]), leak["updated"].replace("<br>", " "))

			if len(info) > padding:
				padding = len(info)

		else:
			leaks.remove(leak)

	print("Fetching {0} leak files...\r\n".format(len(leaks)))
	tikioudiem = tqdm.tqdm(leaks, miniters=1, bar_format="{desc}{n_fmt: >4}/{total_fmt} {percentage:3.0f}%|{bar}|")

	for item in tikioudiem:
		info = "{0} [{1}]".format(html.unescape(item["name"].split("<br><code>")[0]), item["updated"].replace("<br>", " "))
		tikioudiem.set_description(info + "." * (padding - len(info)))
		fetchLeak(session, item)
		sortUnique("{0}.leak".format(item["id"]), "merged.leak")
		os.remove("{0}.leak".format(item["id"]))

	if os.path.isfile("wordlist.txt"):
		print("\r\nFound file 'wordlist.txt'!")
		os.rename("wordlist.txt", "wordlist.old")
		print("Moved to 'wordlist.old'.")
		print("Deduplicating the merged leak file...")
		sortUnique("merged.leak", "wordlist.txt")
		os.remove("merged.leak")
		print("Comparing files for new entries...")
		diff("wordlist.old", "wordlist.txt", "diff.txt")
		os.remove("wordlist.old")
		print("Done!")

	else:
		print("\r\nDeduplicating the merged leak file...")
		sortUnique("merged.leak", "wordlist.txt")
		os.remove("merged.leak")
		print("Done!")


if __name__ == "__main__":
	main()