from webapp.view_helpers import get_mongo
from natsort import natsorted, ns
import random


def get_organized_snps():
    conn = get_mongo()
    docs = list(conn.AdNet.SNPs.find({}, {'chr': 1, 'chr_pos': 1}))
    new_docs = []
    for doc in docs:
        new_docs.append('{}:{}'.format(doc['chr'], doc['chr_pos']))
    return natsorted(new_docs)


def pick_random(prob_list):
  r, s = random.random(), 0
  for num in prob_list:
    s += num[1]
    if s >= r:
      return num[0]

def find_indexes(concerned_snps, organized):
    conn = get_mongo()
    return_dict = {}
    for item in concerned_snps:
        doc = conn.AdNet.SNPs.find_one({'_id': item}, {'chr': 1, 'chr_pos': 1})
        locale = '{}:{}'.format(doc['chr'], doc['chr_pos'])
        index = organized.index(locale)
        return_dict[item] = index
    return return_dict

if __name__ == "__main__":
    s = get_organized_snps()
    data_list = []
    concerned_snps = ['rs1059768', 'rs3740688', 'rs55742290', 'rs199533']
    prob_list = [[1, 0.23], [0, 0.77]]
    for i in range(0, 1000):
        empty_list = []
        for item in range(0, 1954):
            empty_list.append(pick_random(prob_list))
        data_list.append(empty_list)

    indexes = find_indexes(concerned_snps, s)

    for i in range(0, 100):
        data_list[i][1815] = 1
        data_list[i][1394] = 0
        if random.random() < 0.5:
            data_list[i][979] = 1
        if random.random() < 0.5:
            data_list[i][1153] = 1
        data_list[i].append('AD')
    for i in range(0, 900):
        data_list[i+100][1815] = 0
        data_list[i+100].append('Not AD')
    conn = get_mongo()
    for item in data_list:
        conn.AdNet.RiggedData.insert_one({'data': item[0:1954], 'outcome': item[1954]})
