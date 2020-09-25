#!/usr/bin/python3

import html
import json
import multiprocessing
import os
import requests
import tqdm


def createSession():
	headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Referer": "https://temp.hashes.org/", "Connection": "close", "Upgrade-Insecure-Requests": "1"}
	session = requests.Session()
	session.headers.update(headers)
	return session


def queryLeaks(session):
	response = session.get("https://temp.hashes.org/api/data.php?select=leaks")
	leaks = json.loads(response.content.strip().decode('utf-8'))
	return leaks


def fetchLeak(session, leak):
	response = session.get("https://temp.hashes.org/download.php?hashlistId={0}&type=found".format(leak["id"]), stream=True)

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
	print("Fetching {0} leak files...\r\n".format(len(leaks)))

	padding = 0

	for leak in leaks:
		name = html.unescape(leak["name"].split("<code>")[0])

		if len(name) > padding:
			padding = len(name)

	tikioudiem = tqdm.tqdm(leaks, miniters=1, bar_format="{desc}{n_fmt: >4}/{total_fmt} {percentage:3.0f}%|{bar}|")

	for item in tikioudiem:
		name = html.unescape(item["name"].split("<br><code>")[0])
		tikioudiem.set_description(name + "." * (padding - len(name)))
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
