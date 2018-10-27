import re
import os
import time
import os.path
import requests
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


def createOldFile(file):
	timestamp = time.ctime(os.path.getmtime(file))
	outputFile = "{0}-{1}.txt".format(file.split(".")[0], timestamp.replace(" ","-"))
	os.system("mv {0} {1}".format(file, outputFile))
	return outputFile


def findDiffs(oldfile, newfile):
	os.system("comm -13 {0} {1} > wordlistDiff.txt".format(oldfile, newfile))


def main():
	# IDz = ["1049", "1048", "1043", "1036", "855"]
	initialSession = initiateSession()
	IDs = findIDs(initialSession)
	print "List of IDs: {0}".format(IDs)
	print "Fetching {0} files".format(len(IDs))
	for id in IDs:
		createLeakFile(id)
		uniqAndMergeFile("{0}.leakfile".format(id), "merged.leakfile")
		deleteFile("{0}.leakfile".format(id))
	if os.path.isfile("wordlist.txt"):
		print "Found file 'wordlist.txt'"
		oldFile = createOldFile("wordlist.txt")
		print "Created old file '{0}'".format(oldFile)
		uniqAndMergeFile("merged.leakfile", "wordlist.txt")
		deleteFile("merged.leakfile")
		print "Diffing for new passwords"
		findDiffs(oldFile, "wordlist.txt")
		print "Done - written data to 'wordlist.txt' and 'wordlistDiff.txt'"
	else:
		uniqAndMergeFile("merged.leakfile", "wordlist.txt")
		deleteFile("merged.leakfile")
		print "Done - written to 'wordlist.txt'"


if __name__ == "__main__":
	main()
