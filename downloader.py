import urllib.request as urlReq
import threading
import argparse

import time
import math

parser = argparse.ArgumentParser()
parser.add_argument("url_list", metavar='u', nargs='+', help="List of urls to be downloaded.")

args = parser.parse_args()
print_lock = threading.Lock()

downloads = [None] * len(args.url_list)
completed = []

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def showProgress():
	while True:
		if len(downloads) == len(completed):
			break
		for download in downloads:
			if download is not None and download["status"] == False:
				with print_lock:
					print(download["progress"], end="\r")
			time.sleep(1)
				

def downloader(url, thread_num):

	file_name = url.split('/')[-1]

	hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

	req = urlReq.Request(url, headers=hdr)
	u = urlReq.urlopen(req)

	file_size = int(u.getheader("Content-Length"))
	
	print("Thread number: ",thread_num + 1, " File size: ", convert_size(file_size), " | Started successfully")
	print("----------")
	f = open(file_name, 'wb')

	file_size_dl = 0
	block_size = 2**10

	while True:
		buffer = u.read(block_size)
		if not buffer:
			break
		file_size_dl += len(buffer)
		f.write(buffer)
		status = r"%d %s  [%3.2f%%]     " % (thread_num+1, convert_size(file_size_dl), file_size_dl * 100. / file_size)
		dl_status = {}
		dl_status["progress"] = status
		dl_status["status"] = (file_size_dl == file_size)
		with print_lock:
			downloads[thread_num] = dl_status
			if dl_status["status"] == True and thread_num not in completed:
				print(status)
				print("----------")
				completed.append(thread_num)
	
	f.close()

threads = []
id = 0
for url in args.url_list:
	t = threading.Thread(target=downloader, args=(url, id,))
	id += 1
	threads.append(t)	
	t.start()

control_thread = threading.Thread(target=showProgress, args=())
control_thread.start()

for t in threads:
	t.join()
control_thread.join()
