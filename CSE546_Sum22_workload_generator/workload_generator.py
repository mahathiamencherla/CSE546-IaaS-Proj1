import sys
import requests
import os
import argparse
import time

parser = argparse.ArgumentParser(description='Upload images')
parser.add_argument('--num_request', type=int, help='one image per request')
parser.add_argument('--url', type=str, help='URL of your backend server, e.g. http://3.86.108.221/xxxx.php')
parser.add_argument('--image_folder', type=str, help='the path of the folder where images are saved on your local machine')
args = parser.parse_args()

def time_convert(sec):
  mins = sec // 60
  sec = sec % 60
  hours = mins // 60
  mins = mins % 60
  print("Time Lapsed = {0}:{1}:{2}".format(int(hours),int(mins),sec))
  
def send_one_request(url, image_path):
    # Define http payload, "myfile" is the key of the http payload
    file = {"myfile": open(image_path,'rb')} 
    r = requests.post(url, files=file)
    # Print error message if failed
    if r.status_code != 200:
        print('sendErr: '+r.url)
    else :
        image_msg = image_path.split('/')[1] + ' uploaded!'
        msg = image_msg + '\n' + 'Classification result: ' + r.text
        print(msg)
start_time = time.time()
num_request = args.num_request
url = args.url
image_folder = args.image_folder
# Iterate through all the images in your local folder
for i, name in enumerate(os.listdir(image_folder)):
    if i == num_request:
        break
    image_path = image_folder + name
    send_one_request(url, image_path)
    
end_time = time.time()
time_lapsed = end_time - start_time
time_convert(time_lapsed)
