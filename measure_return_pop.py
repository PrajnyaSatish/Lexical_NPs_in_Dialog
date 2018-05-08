# -*- coding: utf-8 -*-
"""
Created on Mon May 07 07:24:39 2018

@author: prajnya
"""
# In[]:
from SwdaParser import Transcript
import re
import glob
from itertools import izip, tee
from matplotlib import pyplot as plt
import numpy as np

# In[]:
def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)


# In[]:

def successive_diff(list_of_line_nums):
    return [y-x for x,y in pairwise(list_of_line_nums)]


# In[]:

reoccur_count = []
all_info = []
metadata = 'swda/swda-metadata.csv'
for name in glob.glob('swda/*/*.csv'):
#for name in glob.glob('swda\sw12utt\sw_1206_2461.utt.csv'):
    trans = Transcript(name, metadata)
    all_utterances = trans.utterances
    lexical_nps = {}
    for utt_no,utt in enumerate(all_utterances):
        pos_tagged_utt = utt.pos
        pos_tagged_split = re.split(' ', pos_tagged_utt)
        pos_tagged_split = [word for word in pos_tagged_split if word]
        pos_tagged_split = [word for word in pos_tagged_split if word not in set(['[',']'])]
        for word_no, word_tag in enumerate(pos_tagged_split):
            if 'NNP' in word_tag:
                word,tag = re.split('/',word_tag)
                if len(word)>1:
                    if word not in lexical_nps:
                        lexical_nps.update({word:{'filename':name, 'count':1,'line_num':[utt_no]}})
                    else:
                        lexical_nps[word]['count']+=1
                        if utt_no not in lexical_nps[word]['line_num']:
                            lexical_nps[word]['line_num'].append(utt_no)
    for np_word in lexical_nps.iterkeys():
        if len(lexical_nps[np_word]['line_num']) > 1:
            diff_list = successive_diff(lexical_nps[np_word]['line_num'])
            reoccur_count.extend(diff_list)
            lexical_nps[np_word].update({'line_distances':diff_list})
    all_info.append(lexical_nps)
        
        

# In[]:
plt.rcParams["figure.figsize"] = (20,12)
y_range,x_range,_ = plt.hist(reoccur_count,bins = 375, range=[1,375], color='blue')
plt.yticks(range(0, 1100, 100))
plt.xticks(range(0, max(reoccur_count)+1, 75))
plt.xlabel('Distance between successive utterances of the same lexical NP', fontsize=18)
plt.ylabel('Frequency', fontsize=18)
#plt.title('Count of distance between successive utterances of same lexical NP \nvs frequency of distances between successive NP returns.', fontsize=24)
#plt.show()
plt.savefig('reoccur_plot.png', bbox_inches='tight',dpi=300)


# In[]:
from prettytable import PrettyTable
table = PrettyTable()

p_50 = np.percentile(reoccur_count, 50, interpolation="nearest")
std_dev = round(np.std(reoccur_count),2)
mean = round(np.mean(reoccur_count),2)
median = np.median(reoccur_count)
table.field_names = ["Stats",'Values']
table.align['Stats']="l"
table.add_row(["Mean", mean])
table.add_row(["Median", median])
table.add_row(["Std Dev", std_dev])
table.add_row(["50th %ile", p_50])


print(table)
# In[]:
to_write_string = ''
for dialog in all_info:
    for proper_noun in dialog.iterkeys():
        if 'line_distances' in dialog[proper_noun]:
            for distances in dialog[proper_noun]['line_distances']:
                if distances in range(250,400):
                    to_write_string+='\n\n'
                    header_string = str(proper_noun) + ', '+ str(dialog[proper_noun]['filename']) + ', '+ str(dialog[proper_noun]['line_num'])+ ', '+ str(dialog[proper_noun]['line_distances'])+'\n'
                    to_write_string+=header_string
                    transcripts = Transcript(dialog[proper_noun]['filename'], metadata)
                    all_utterances = transcripts.utterances
                    for line_no, utt in enumerate(all_utterances):
                        utterance_string = '{2} - {0}: {1}\n'.format(utt.caller, utt.text, line_no)
                        to_write_string+=utterance_string
#print to_write_string

write_file = 'distance_250-400.txt'
with open(write_file,'w') as wf:
    wf.write(to_write_string)                        
                


# In[]:
sorted_count = sorted(reoccur_count)



