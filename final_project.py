import urllib3
import urllib.request
import numpy as np
from bs4 import BeautifulSoup #https://stackoverflow.com/questions/11023530/python-to-list-http-files-and-directories
import requests
import os
import pandas as pd
import matplotlib.pyplot as plt

column_names = {'local_relative_humidity': 30, 'local_relative_humidity_uncertainty': 32}    
base_url = 'https://atmos.nmsu.edu/PDS/data/mslrem_1001/DATA/'
sol_epoch_starts = np.array([1, 90, 180, 270, 360, 450, 584, 708, 805, 939, 1063, 1160, 1294, 1418, 1515, 1649, 1773, 1870, 2004, 2128, 2225, 2359])
# num_epochs = sol_epoch_starts.size - 1
num_epochs = 1

def listFD(url, ext=''):
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    return [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]

def get_epoch_name(index):
    string1 = str(sol_epoch_starts[index]) 
    string2 = str(sol_epoch_starts[index+1] - 1)
    string1 = '0' * (5 - len(string1)) + string1    
    string2 = '0' * (5 - len(string2)) + string2
    entire_string = 'SOL_' + string1 + '_' + string2
    return entire_string  

def get_sol_name(sol_num):
    string = str(sol_num)
    string = 'SOL' + '0' * (5 - len(string)) + string
    return string


http = urllib3.PoolManager()
data_all = []
for epoch_index in range(num_epochs):                            
    epoch_file_name = get_epoch_name(epoch_index)
#     print(epoch_file_name)
    for sol_number in range(sol_epoch_starts[epoch_index], sol_epoch_starts[epoch_index+1]):
        sol_file_name = get_sol_name(sol_number)
#         print("LOOK HERE:", 'base', base_url, 'epoch file', epoch_file_name, 'sol', sol_file_name)
        entire_url = base_url + epoch_file_name + '/' + sol_file_name
        entire_list = listFD(entire_url)
        for file_name in entire_list:
            if ('RMD' in file_name) and ('TAB' in file_name):
                final_file_name = file_name
                r = http.request('GET', final_file_name)
                data = r.data.decode('utf-8')
                data = data.split('\n')
                data_all += [line.split(',') for line in data]
                break
# print(*data[:10], sep = '\n')
df = pd.DataFrame(data_all)
df = df[[0, 11, 12, 13, 14, 15, 16, 30, 31, 32]]
df = df.replace('    UNK', np.nan)
df = df.dropna()

epoch_index = 1
epoch_file_name = get_epoch_name(epoch_index)
for sol_number in range(sol_epoch_starts[epoch_index], sol_epoch_starts[epoch_index+1]):
    sol_file_name = get_sol_name(sol_number)
    entire_url = base_url + epoch_file_name + '/' + sol_file_name
    entire_list = listFD(entire_url)
    for file_name in entire_list:
        if ('RMD' in file_name) and ('TAB' in file_name):
            final_file_name = file_name
            r = http.request('GET', final_file_name)
            data = r.data.decode('utf-8')
            data = data.split('\n')
            data_all += [line.split(',') for line in data]
            break
df_temp = pd.DataFrame(data_all)
df_temp = df_temp[[0, 11, 12, 13, 14, 15, 16, 30, 31, 32]]
df = pd.concat([df, df_temp])
df = df.replace('    UNK', np.nan)
df = df.dropna()

plt.plot(df[11], df[30])
plt.show(block=True)