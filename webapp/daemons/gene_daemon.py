from itertools import islice

import pandas
import requests
import json
import re
import collections
from multiprocessing import Pool
from timeit import default_timer as timer
import os, sys, subprocess
from Bio import SeqIO
import xmltodict
from pymongo.errors import ServerSelectionTimeoutError
from webapp.view_helpers import get_mongo


class GeneDaemon:
    api_key = "baf3baa6f018c25575f11632ceea1257e808"
    headers = {'Accept': 'application/json'}
    sample_gene_doc = {
        'name': None,
        '_id': None,
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
        'mod_len': 0,
        'nm_len': 0,
        'snp_effects': []
    }
    gene_data = []
    rna_data = []
    genes = []
    gene_docs = {}
    syns = {}
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
            self.download_dataset(f)
            self.get_syns_and_data(10)
            args = ('j', '', 10)
        if args[0] == 'j':
            # this means we have json data hurrah
            # third arg is num of processes
            self.read_in_names('daemons/gene_name_list.txt')
            self.get_syns_and_data(10)
            self.get_genes(f)
            self.pull_gene_data_process(int(args[2]))


    def read_in_names(self, f):
        f = open(f, 'r')
        self.genes = f.read().split("\n")
        f.close()

    def divide_data(self, n):
        for i in range(0, len(self.genes), n):
            yield self.genes[i:i+n]

    def get_syns_and_data(self, n):
        smaller = list(self.divide_data(n))
        with Pool() as pool:
            res = pool.map(self.pull_syn_data, smaller)
        for item in res:
            for syn in item.keys():
                self.syns[syn] = item[syn]

    def convert_names_to_ids(self, n):
        smaller = list(self.divide_data(n))
        start = timer()
        with Pool() as pool:
            res = pool.map(self.pull_id_data, smaller)
        end = timer()
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

    def pull_syn_data(self, data):
        to_ret = {}
        #| ./dataformat tsv gene --fields gene-id'
        for gene in data:
            command = ['./datasets', 'summary', 'gene', 'symbol', '{}'.format(gene), '--taxon', '9606', '--as-json-lines']
            ps = subprocess.Popen(command, stdout=subprocess.PIPE)
            output = json.loads(ps.communicate()[0].decode('utf-8'))
            try:
                num = int(output['gene']['gene_id'])
                if 'synonyms' in output['gene'].keys() and len(output['gene']['synonyms']) != 0:
                    to_ret[num] = output['gene']['synonyms']
            except KeyError as e:
                if output['warnings'][0]['gene_warning_code'] == 'UNRECOGNIZED_GENE_SYMBOL':
                    pass
            except Exception as e:
                print(e)
        return to_ret

    def pull_id_data(self, data):
        to_ret = []
        #| ./dataformat tsv gene --fields gene-id'
        for gene in data:
            command = ['./datasets', 'summary', 'gene', 'symbol', '{}'.format(gene), '--taxon', '9606', '--as-json-lines']
            ps = subprocess.Popen(command, stdout=subprocess.PIPE)
            output = json.loads(ps.communicate()[0].decode('utf-8'))
            try:
                num = int(output['gene']['gene_id'])
                if 'synonyms' in output['gene'].keys() and len(output['gene']['synonyms']) != 0:
                    self.syns[num] = output['gene']['synonyms']
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
        new_genes = []
        for gene in genes:
            if gene != '':
                new_genes.append(gene)
        genes = new_genes
        for gene in genes:
            doc = self.sample_gene_doc.copy()
            g = self.gene_data[gene]
            try:
                type = g['type']
            except KeyError:
                type = ''
            doc['name'] = g['symbol']
            doc['_id'] = int(gene)
            doc['description'] = g['description']
            doc['chromosome'] = g['chromosomes'][0]
            doc['expression'] = self.get_expression_vals(gene)
            doc['type'] = type
            try:
                doc['authority'] = g['nomenclatureAuthority']['authority']
                doc['identifier']= g['nomenclatureAuthority']['identifier']
                doc['link'] = "https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/{}".format(doc['identifier'])
            except:
                doc['authority']= ''
                doc['identifier']= ''
            try:
                doc['rna_sequences']= self.rna_data[int(gene)]
            except:
                doc['rna_sequences'] = []
            try:
                doc['range']= g['genomicRanges'][0]['range'][0]
            except:
                doc['range'] = {'begin': None, 'end': None, 'orientation': None}
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
        if doc['authority'] == 'HGNC':
            self.get_protein_info(doc)
        return doc

    def get_protein_info(self, doc):
        doc = self.get_hgnc_data(doc['_id'], doc)
        doc = self.get_uniprot_data(doc)
        return doc


    def get_hgnc_data(self, gene_id, doc):
        id = doc['identifier'].split(':')[1]
        url = 'https://rest.genenames.org/fetch/hgnc_id/{}'.format(id)
        content = requests.get(url).content
        dict_data = xmltodict.parse(content)
        try:
            uniprot_id = list(filter(lambda record: record['@name'] == 'uniprot_ids', dict_data['response']['result']['doc']['arr']))[0]['str']
            doc['uniprot_id'] = uniprot_id
        except Exception as e:
            pass
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
        if 'comments' not in content.keys():
            content['comments'] = []
        for comment in content['comments']:
            if 'commentType' in comment.keys():
                if comment['commentType'] == 'CATALYTIC ACTIVITY':
                    if 'catalytic_activity' in doc.keys() and comment['reaction']['name'] not in doc['catalytic_activity']:
                        doc['catalytic_activity'].append(comment['reaction']['name'])
                    doc['catalytic_activity'] = [comment['reaction']['name']]
                if comment['commentType'] == 'COFACTOR':
                    cofactors = []
                    for item in comment['cofactors']:
                        cofactors.append(item['name'])
                    doc['cofactors'] = cofactors
                if comment['commentType'] == 'SUBCELLULAR LOCATION':
                    locations = []
                    for location in comment['subcellularLocations']:
                        locations.append(location['location']['value'])
                    doc['locations'] = locations
        return doc

    def annotate_snp_data(self, doc):
        doc['snp_list'] = {'modifying': [], 'non_modifying': []}
        mc = get_mongo()
        total_genes = [doc['name']]
        if doc['_id'] in self.syns.keys():
            total_genes += self.syns[doc['_id']]
        for gene in total_genes:
            snps = mc.AdNet.SNPs.find({'genes': '{}'.format(gene)})
            for snp in snps:
                if snp['risk_level'] == 'MODIFIER':
                    doc['snp_list']['modifying'].append(snp['_id'])
                else:
                    amino_acid, affected_features = self.pull_amino_acid_index(snp, doc)
                    doc['snp_effects'].append({'snp': snp['_id'], 'amino_acid': amino_acid, 'affected_features': affected_features})
                    doc['snp_list']['non_modifying'].append(snp['_id'])
        doc['mod_len'] = len(doc['snp_list']['modifying'])
        doc['nm_len'] = len(doc['snp_list']['non_modifying'])
        return doc

    def find_correct_consequence(self, cons, snp):
        parsed = []

        #remove consequences that don't match ncbi functional class of snp
        for item in cons:
            consequences_list = item['molecularConsequences']
            add = 0
            for consequence in consequences_list:
                if consequence == snp['functional_class']:
                    add = 1
            if add == 1:
                parsed.append(item)
        if len(parsed) == 0:
            print(snp['_id'])
            parsed = cons

        count_list = []
        #create new list with condensed dict information if duplicates of dict item in list update count
        for item in parsed:
            new_dict = {}
            new_dict['aminoAcidChange'] = item['aminoAcidChange']
            new_dict['codonChange'] = item['codonChange']
            new_dict['position'] = item['proteinStartPosition']
            new_dict['polyphenPrediction'] = item['polyphenPrediction']
            new_dict['siftPrediction'] = item['siftPrediction']
            count_list.append(new_dict)
        c = collections.Counter(json.dumps(l) for l in count_list).most_common()
        try:
            data = json.loads(c[0][0])
            i = int(data['position'])
        except Exception as e:
            return 0
        return i


    def pull_amino_acid_index(self, snp, gene):
        url = 'https://www.alliancegenome.org/api/variant/{}'.format(snp['_id'])
        content = json.loads(requests.get(url).content.decode('utf8'))
        num = self.find_correct_consequence(content['transcriptLevelConsequence'], snp)
        affected_features = []
        try:
            if num != 0:
                for feature in gene['protein_features']:
                    start = feature['location']['start']['value']
                    end = feature['location']['end']['value']
                    if feature['type'] in self.feature_types and start != None and end != None and start <= num <= end:
                        affected_features.append(feature)
        except Exception as e:
            print(e)
            return 'Unknown', 'Unknown'
        if num == 0:
            return 'Unknown', 'Unknown'
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
                    {'_id': {'$ne': new_data['_id']}},
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
                    {'snp_effects': {'$ne': new_data['snp_effects']}},
                    {'mod_len':{'$ne': new_data['mod_len']}},
                    {'nm_len': {'$ne': new_data['nm_len']}},
                ]},
                {'$set': {
                    '_id': new_data['_id'],
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
                    'snp_effects': new_data['snp_effects'],
                    'mod_len': new_data['mod_len'],
                    'nm_len': new_data['nm_len']
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