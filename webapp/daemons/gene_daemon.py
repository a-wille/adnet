from itertools import islice

import pandas
import requests
import json
import re
import os, sys
from multiprocessing import Pool
from timeit import default_timer as timer
import os, sys, subprocess
from Bio import SeqIO
import xmltodict
from pymongo.errors import ServerSelectionTimeoutError
from webapp.extra.view_helper import get_mongo


class GeneDaemon:
    api_key = "baf3baa6f018c25575f11632ceea1257e808"
    headers = {'Accept': 'application/json'}
    sample_gene_doc = {
        'name': None,
        'id': None,
        'description': None,
        'chromosome': None,
        'expression': {},
        'type': None,
        'authority': None,
        'identifier': None,
        'rna_sequences': None,
        'range': None,
        'uniprot_id': None,
        'protein_features': None,
        'protein_description': None,
        'sequence': None,
        'catalytic_activity': [],
        'cofactors': None,
        'locations': None,
        'snp_list': {'non_modifying': [], 'modifying': []},
        'amino_acid_index': None,
        'affected_features': {}
    }
    gene_data = []
    rna_data = []
    genes = []
    gene_docs = {}
    feature_types = types = ['Signal', 'Peptide', 'Chain', 'Propeptide', 'Transit peptide', 'DNA binding',
                 'Motif', 'Lipidation', 'Modified residue', 'Non-standard reside', 'Cross-link',
                 'Glycosylation', 'Disulfide bond', 'Site', 'Helix', 'Turn', 'Beta strand',
                 'Region', 'Domain', 'Binding site', 'Active site', 'Motif']

    def __init__(self, *args):
        """never init GeneDaemon without running SNP Daemon first to get list of genes"""
        if len(args) > 1:
            f = args[1]
        relative_path = '../'
        os.chdir(os.path.join(os.path.abspath(sys.path[0]), relative_path))
        if args[0] == 's':
            # this means that we are loading in the string name id file, nothing else is generated
            self.read_in_names(f)
            #default file name genes.txt
            self.convert_names_to_ids(10)
            #default file name gene_id_list.txt
            args = ('i', None)
            f = 'daemons/gene_id_list.txt'
        if args[0] == 'i':
            # this means that we are loading in the number id file
            self.get_genes(f)
            self.download_dataset(f)
            args = ('j', 10)
        if args[0] == 'j':
            # this means we have json data hurrah so second arg should be num of jobs in proc
            # third arg is num of processes
            self.get_genes(f)
            self.pull_gene_data_process(int(args[2]))


    def read_in_names(self, f):
        f = open(f, 'r')
        self.genes = f.read().split("\n")
        f.close()

    def divide_data(self, n):
        for i in range(0, len(self.genes), n):
            yield self.genes[i:i+n]

    def convert_names_to_ids(self, n):
        smaller = list(self.divide_data(n))
        start = timer()
        with Pool() as pool:
            res = pool.map(self.pull_id_data, smaller)
        end = timer()
        print(f'elapsed time: {end - start}')
        f = open('daemons/gene_id_list.txt', 'w')
        for item in res:
            for id in item:
                f.write(str(id) + '\n')
        f.close()

    def get_genes(self, f):
        f = open(f, 'r')
        try:
            self.genes = f.read().split("\n")
            f.close()
        except:
            exit()

    def pull_id_data(self, data):
        to_ret = []
        #| ./dataformat tsv gene --fields gene-id'
        for gene in data:
            command = ['./datasets', 'summary', 'gene', 'symbol', '{}'.format(gene), '--taxon', '9606', '--as-json-lines']
            ps = subprocess.Popen(command, stdout=subprocess.PIPE)
            output = json.loads(ps.communicate()[0].decode('utf-8'))
            try:
                num = int(output['gene']['gene_id'])
                to_ret.append(num)
            except KeyError as e:
                if output['warnings'][0]['gene_warning_code'] == 'UNRECOGNIZED_GENE_SYMBOL':
                    pass
            except Exception as e:
                print(e)
        return to_ret

    def download_dataset(self, f):
        base_command = './datasets download gene gene-id --inputfile {} && unzip -o ncbi_dataset.zip'
        command = base_command.format(f)
        x = subprocess.Popen(command, shell=True)
        x.wait()


    def pull_gene_data_process(self, n):
        self.gene_data = self.pull_json_data()
        self.rna_data = self.pull_rna_data()
        smaller = list(self.divide_data(n))
        start = timer()
        with Pool() as pool:
            res = pool.map(self.pull_gene_data, smaller)
        end = timer()
        print(f'elapsed time: {end - start}')


    def pull_json_data(self):
        f = open('ncbi_dataset/data/data_report.jsonl', 'r')
        json_list = list(f)
        data = {}
        for item in json_list:
            result = json.loads(item)
            data[result['geneId']] = result
        return data


    def pull_rna_data(self):
        data = {}
        seqs = SeqIO.parse(open('ncbi_dataset/data/rna.fna'),'fasta')
        for record in seqs:
            id = int(record.description.split('GeneID=')[1].split(']')[0])
            if id in data.keys():
                used = 0
                for s in data[id]:
                    if s['seq'] == str(record.seq):
                        used = 1
                if used == 0:
                    if record.description.find('transcript') != -1:
                        data[id].append({'transcript': record.description.split('transcript=')[1].split(']')[0], 'seq': str(record.seq)})
                    else:
                        data[id].append({'transcript': 1, 'seq': str(record.seq)})
            else:
                if record.description.find('transcript') != -1:
                    data[id] = [{'transcript': record.description.split('transcript=')[1].split(']')[0], 'seq': str(record.seq)}]
                else:
                    data[id] = [{'transcript': 1, 'seq': str(record.seq)}]
        return data


    def pull_gene_data(self, genes):
        docs = []
        for gene in genes:
            doc = self.sample_gene_doc.copy()
            g = self.gene_data[gene]
            try:
                type = g['type']
            except KeyError as e:
                type = ''
            doc['name'] = g['symbol']
            doc['id'] = int(gene)
            doc['description'] = g['description']
            doc['chromosome'] = g['chromosomes'][0]
            doc['expression'] = self.get_expression_vals(gene)
            doc['type'] = type
            try:
                doc['authority'] = g['nomenclatureAuthority']['authority'],
                doc['identifier']= g['nomenclatureAuthority']['identifier'],
            except:
                doc['authority']= '',
                doc['identifier']= '',
            try:
                doc['rna_sequences']= self.rna_data[int(gene)]
            except:
                doc['rna_sequences'] = []
            try:
                doc['range']= g['genomicRanges'][0]['range'][0]
            except:
                doc['range'] = {}
            if doc['type'] == 'PROTEIN_CODING':
                doc = self.try_protein_info(doc)
                doc = self.annotate_snp_data(doc)
            self.update_mongo_doc(doc)
            docs.append(doc)
        return docs

    def get_expression_vals(self, gene):
        possible_bases = ['PRJEB4337', 'PRJEB2445', 'PRJNA270632', 'PRJNA280600']
        base_url = 'https://ncbi.nlm.nih.gov/projects/Gene/download_expression.cgi?PROJECT_DESC={}&GENE={}'
        tissues = ['adrenal', 'appendix', 'bone marrow', 'brain', 'colon', 'duodenum', 'endometrium',
                   'esophagus', 'fat', 'gall bladder', 'heart', 'kidney', 'liver', 'lung',
                   'lymph node', 'ovary', 'pancreas', 'placenta', 'salivary gland', 'skin',
                   'small intestine', 'spleen', 'stomach', 'testis', 'thyroid', 'urinary bladder']
        data = {}
        for base in possible_bases:
            url = base_url.format(base, gene)
            content = requests.get(url).content.decode('utf8')
            lines = content.split('\n')
            try:
                if len(lines[3].split('\t')) > 20:
                    headers = lines[3].split('\t')
                    values = lines[4].split('\t')
                    for tissue in tissues:
                        if tissue in headers:
                            data[tissue] = values[headers.index(tissue)]
                    return data
            except ValueError as v:
                print(v)
        return data

    def try_protein_info(self, doc):
        """either HGNC is the authority, or no Authority is listed"""
        if doc['authority'][0] == 'HGNC':
            self.get_protein_info(doc)
        return doc

    def get_protein_info(self, doc):
        doc = self.get_hgnc_data(doc['id'], doc)
        doc = self.get_uniprot_data(doc)
        return doc


    def get_hgnc_data(self, gene_id, doc):
        id = doc['identifier'][0].split(':')[1]
        url = 'https://rest.genenames.org/fetch/hgnc_id/{}'.format(id)
        content = requests.get(url).content
        dict_data = xmltodict.parse(content)
        try:
            uniprot_id = list(filter(lambda record: record['@name'] == 'uniprot_ids', dict_data['response']['result']['doc']['arr']))[0]['str']
            doc['uniprot_id'] = uniprot_id
        except Exception as e:
            print("ope")
        return doc

    def get_uniprot_data(self, doc):
        uniprot_id = doc['uniprot_id']
        if isinstance(uniprot_id, list):
            uniprot_id = uniprot_id[0]
        url = 'https://rest.uniprot.org/uniprotkb/{}'.format(uniprot_id)
        content =  requests.get(url).json()
        try:
            doc['protein_features'] = content['features']
        except KeyError as e:
            doc['protein_features'] = []
        try:
            doc['protein_description'] = content['proteinDescription']['recommendedName']['fullName']['value']
        except KeyError as e:
            doc['protein_description'] = None
        try:
            doc['sequence'] = content['sequence']['value']
        except KeyError as e:
            doc['sequence'] = None
        if 'comment' not in content.keys():
            content['comments'] = []
        for comment in content['comments']:
            if 'commentType' in comment.keys():
                if comment['commentType'] == 'CATALYTIC ACTIVITY':
                    if 'catalytic_activity' in doc.keys() and comment['reaction']['name'] not in doc['catalytic_activity']:
                        doc['catalytic_activity'].append(comment['reaction']['name'])
                    doc['catalytic_activity'] = list(comment['reaction']['name'])
                if comment['commentType'] == 'COFACTOR':
                    cofactors = []
                    for item in comment['cofactors']:
                        cofactors.append(item['name'])
                    doc['cofactors'] = cofactors
                if comment['commentType'] == 'SUBCELLULAR LOCATION':
                    locations = []
                    for location in comment['subcellularLocations']:
                        locations.append(location['location']['value'])
                    doc['subcellular_locations'] = locations
        return doc

    def annotate_snp_data(self, doc):
        doc['snp_list'] = {'modifying': [], 'non_modifying': []}
        mc = get_mongo()
        snps = mc.AdNet.SNPs.find({'genes': '{}'.format(doc['name'])})
        for snp in snps:
            if snp['risk_level'] == 'MODIFIER':
                doc['snp_list']['modifying'].append(snp['snp_name'])
            else:
                amino_acid, affected_features = self.pull_amino_acid_index(snp, doc)
                doc['amino_acid_index'] = amino_acid
                doc['affected_features'][snp['snp_name']] = affected_features
                doc['snp_list']['non_modifying'].append(snp['snp_name'])
        return doc

    def pull_amino_acid_index(self, snp, gene):
        file = 'dbSNP_snp_list.tsv'
        df = pandas.read_csv(file, sep='\t')
        rows = df.loc[df['SNP'] == snp['snp_name']]
        changes = rows['AMINO_ACID_CHANGE']
        #get most common record value
        common_list = {}
        for item in changes:
            if item not in common_list.keys():
                common_list[item] = 1
            else:
                common_list[item] += 1
        try:
            index = max(common_list, key=common_list.get)
            num = int(re.findall(r'\d+', index)[0]) - 1
            orig_acid = index.split(str(num + 1))[0]
            if orig_acid != gene['sequence'][num]:
                if orig_acid == gene['sequence'][num - 1]:
                    num -= 1
                else:
                    if orig_acid == gene['sequence'][num - 1]:
                        num -= 1
                    else:
                        print("What")
        except ValueError as e:
            print("oopsies")
            print(common_list)
            print(e)
            num = 0

        affected_features = []

        for feature in gene['protein_features']:
            if feature['type'] in self.feature_types and feature['location']['start']['value'] <= num <= feature['location']['end']['value']:
                affected_features.append(feature)
        if affected_features != []:
            print("yay")
        return num, affected_features

    def update_mongo_doc(self, new_data):
        #update only if fields are new/different from mongo record
        #if no record, inserts new doc
        upsert = True
        conn = get_mongo()
        doc = conn.AdNet.Genes.find_one({'name': new_data['name']})
        if doc:
            upsert = False
        try:
            conn.AdNet.Genes.find_one_and_update(
                {'name': new_data['name'],
                '$or': [
                    {'id': {'$ne': new_data['id']}},
                    {'description': {'$ne': new_data['description']}},
                    {'chromosome': {'$ne': new_data['chromosome']}},
                    {'type': {'$ne': new_data['type']}},
                    {'authority': {'$ne': new_data['authority']}},
                    {'identifier': {'$ne': new_data['identifier']}},
                    {'rna_sequences': {'$ne': new_data['rna_sequences']}},
                    {'range': {'$ne': new_data['range']}},
                    {'protein_features': {'$ne': new_data['protein_features']}},
                    {'protein_description': {'$ne': new_data['protein_description']}},
                    {'sequence': {'$ne': new_data['sequence']}},
                    {'catalytic_activity': {'$ne': new_data['catalytic_activity']}},
                    {'cofactors': {'$ne': new_data['cofactors']}},
                    {'locations': {'$ne': new_data['locations']}},
                    {'snp_list': {'$ne': new_data['snp_list']}},
                    {'amino_acid_index': {'$ne': new_data['amino_acid_index']}},
                    {'affected_features': {'$ne': new_data['affected_features']}}
                ]},
                {'$set': {
                    'id': new_data['id'],
                    'description': new_data['description'],
                    'chromosome': new_data['chromosome'],
                    'expression': new_data['expression'],
                    'type': new_data['type'],
                    'authority': new_data['authority'],
                    'identifier': new_data['identifier'],
                    'rna_sequences': new_data['rna_sequences'],
                    'range': new_data['range'],
                    'protein_features': new_data['protein_features'],
                    'protein_description': new_data['protein_description'],
                    'sequence': new_data['sequence'],
                    'catalytic_activity': new_data['catalytic_activity'],
                    'cofactors': new_data['cofactors'],
                    'locations': new_data['locations'],
                    'snp_list': new_data['snp_list'],
                    'amino_acid_index': new_data['amino_acid_index'],
                    'affected_features': new_data['affected_features']
                }}, upsert=upsert
            )
        except ServerSelectionTimeoutError as e:
            print("What")
        except Exception as f:
            print("confused")

    def divide_gene_list(self, n):
        it = iter(self.genes)
        for i in range(0, len(self.genes), n):
            yield {k: self.genes[k] for k in islice(it, n)}


d = GeneDaemon('j', 'daemons/gene_id_list.txt', 10)