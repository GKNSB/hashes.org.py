Python3 script that downloads all cracked passwords from leaks on temp.hashes.org and merges them into a single wordlist.txt file.
When wordlist.txt already exists, renames it, creates the new one and diffs them, resulting in diff.txt that contains all the new words between the two files.
Meant to run on linux with python3.

Dependencies:

pip install requests,tqdm

Latest time the script was run on 28/09/2020 
* Retrieved unique passwords 878.610.690 
* breachcompilation unique passwords 384.153.427 
