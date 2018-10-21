import requests
import re
import os
import multiprocessing

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Referer": "https://hashes.org/", "Connection": "close", "Upgrade-Insecure-Requests": "1"}
s = requests.Session()


def initiateSession():
	response = s.get("https://hashes.org/leaks.php")
	return response.content


def findIDs(content):
	regex = "download\.php\?hashlistId=(\d+)\&type=hfound"
	return re.findall(regex, content)


def createLeakFile(id):
	url = "https://hashes.org:443/download.php?hashlistId={0}&type=found".format(id)
	print "Fetching {0}".format(url)
	response = s.get(url, headers=headers, stream=True)
	with open("{0}.leakfile".format(id), "wb") as f:
		for chunk in response.iter_content(chunk_size=1024):
			if chunk:
				f.write(chunk)


def mergeFile(file, fileName):
	with open(file, "r") as openFile:
		with open(fileName, "a") as mergedFile:
			for line in openFile:
				mergedFile.write(line)


def uniqAndMergeFile(sourceFile, targetFile):
	coreCount = multiprocessing.cpu_count()
	os.system("sort -u --parallel={0} {1} >> {2}".format(coreCount, sourceFile, targetFile))


def deleteFile(file):
	os.remove(file)


def renameFile(file1, file2):
	os.rename(file1, file2)


def main():
	initialSession = initiateSession()
	IDs = findIDs(initialSession)
	print "List of IDs: {0}".format(IDs)
	print "Fetching {0} files".format(len(IDs))
	for id in IDs:
		createLeakFile(id)
		uniqAndMergeFile("{0}.leakfile".format(id), "merged.leakfile")
		deleteFile("{0}.leakfile".format(id))
	uniqAndMergeFile("merged.leakfile", "wordlist.txt")
	deleteFile("merged.leakfile")


if __name__ == "__main__":
	main()
