import requests
import json
from multiprocessing import Pool
from timeit import default_timer as timer
from itertools import islice
import os, sys, subprocess
from Bio import SeqIO


class GeneDaemon:
    api_key = "baf3baa6f018c25575f11632ceea1257e808"
    headers = {'Accept': 'application/json'}
    data = None
    genes = []
    docs = {}
    gen_data = []
    rna_data = []


    def __init__(self):
        url = 'https://www.ebi.ac.uk/gwas/rest/api/efoTraits/{}'.format(self.trait_id)
        req = requests.get(url, headers=self.headers).json()
        url = req['_links']['associationsByTraitSummary']['href']
        self.data = requests.get(url, headers=self.headers).json()
        f = open('genes.txt', 'r')
        self.genes = f.read().split("\n")
        f.close()
        relative_path = '../'
        os.chdir(os.path.join(os.path.abspath(sys.path[0]), relative_path))


    def __init__(self, f):
        f = open(f, 'r')
        try:
            self.genes = f.read().split("\n")
            f.close()
            relative_path = '../'
            os.chdir(os.path.join(os.path.abspath(sys.path[0]), relative_path))
        except:
            exit()


    def load_gene_data(self):
        f = open('gene_daemon/gene_docs.json','r')
        data = json.load(f)
        return data


    def pull_id_data(self, data):
        count = 0
        to_ret = []
        base_command = './datasets summary gene symbol {} --taxon 9606 --as-json-lines | ./dataformat tsv gene --fields gene-id'
        for gene in data:
            command = base_command.format(gene)
            ps = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = ps.communicate()[0].decode("utf-8").split('\n')
            if len(output) != 3 or output[2] != '':
                if output[1] == '':
                    print("GeneID {} NOT FOUND".format(gene))
                    count += 1
            else:
                to_ret.append(output[1])
        return to_ret

    def divide_data(self, n):
        for i in range(0, len(self.genes), n):
            yield self.genes[i:i+n]

    def pull_gene_ids(self, n):
        smaller = list(self.divide_data(n))
        start = timer()
        with Pool() as pool:
            res = pool.map(self.pull_id_data, smaller)
        end = timer()
        print(f'elapsed time: {end - start}')
        f = open('gene_id_list.txt', 'w')
        for item in res:
            for id in item:
                f.write(id + '\n')
        f.close()

    def get_gene_data_job(self, n):
        self.gen_data = self.pull_json_data()
        self.rna_data = self.pull_rna_data()
        smaller = list(self.divide_data(n))
        start = timer()
        with Pool() as pool:
            res = pool.map(self.pull_gene_data, smaller)
        end = timer()
        print(f'elapsed time: {end - start}')
        all = []
        for item in res:
            for record in item:
                all.append(record)
        f = open('gene_docs.json', 'w')
        for item in all:
            f.write(json.dumps(item) + "\n")
        f.close()


    def download_dataset(self, f):
        base_command = './datasets download gene gene-id --inputfile gene_daemon/{} && unzip -o ncbi_dataset.zip'
        command = base_command.format(f)
        x = subprocess.Popen(command, shell=True)
        x.wait()


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
                    # data[tissue] = values[headers.index(tissue)]
                    return data
            except ValueError as v:
                print(v)
        return data


    def pull_gene_data(self, genes):
        docs = []
        for gene in genes:
            g = self.gen_data[gene]
            doc = {
                'name': g['symbol'],
                'id': int(gene),
                'description': g['description'],
                'chromosome': int(g['chromosomes'][0]),
                # gotta figure out why there are multiple possible locations for a gene range
                # for now, we just pick one and smile (with accession version
                'expression': self.get_expression_vals(gene),
                'type': g['type'],
            }
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
            docs.append(doc)
        return docs





class SNPDaemon:
    trait_id = "MONDO_0004975"
    headers = {'Accept': 'application/json'}
    data = None
    snps = []
    snp_data = {}
    genes = []
    docs = {}


    def __init__(self):
        url = 'https://www.ebi.ac.uk/gwas/rest/api/efoTraits/{}'.format(self.trait_id)
        req = requests.get(url, headers=self.headers).json()
        url = req['_links']['associationsByTraitSummary']['href']
        self.data = requests.get(url, headers=self.headers).json()
        f = open('genes.json', 'w')
        f.write(json.dumps(self.data))
        f.close()
        self.get_snps()


    def __init__(self, f):
        f = open(f, 'r')
        try:
            self.data = json.load(f)
            f.close()
        except:
            exit()
        self.get_snps()


    def get_snps(self):
        count = 0
        associations = self.data['_embedded']['associations']
        for association in associations:
            for snp in association['snps']:
                doc = {}
                risk_list = []
                for loci in association['loci']:
                    for allele in loci['strongestRiskAlleles']:
                        a = {}
                        try:
                            a['risk_freq'] = association['riskFrequency']
                            a['risk_allele_name'] = allele['riskAlleleName']
                            a['risk_allele_value'] = allele['riskAlleleName'].split('-')[1]
                            risk_list.append(a)
                        except Exception as e:
                            print(e)
                #sometimes double reported values from different experiments on an SNP so fuck that
                doc['strongest_risk_alleles'] = risk_list
                if snp['rsId'] in self.snp_data:
                    for item in doc['strongest_risk_alleles']:
                        if item not in self.snp_data[snp['rsId']]['strongest_risk_alleles']:
                            self.snp_data[snp['rsId']]['strongest_risk_alleles'] += doc['strongest_risk_alleles']

                # if count < 20:
                self.snp_data[snp['rsId']] = doc
                    # count += 1


    def pull_snp_data(self, data):
        ret = []
        for snp in data:
            doc = data[snp]
            snp_url = 'https://www.ebi.ac.uk/gwas/rest/api/singleNucleotidePolymorphisms/{}'.format(snp)
            snp_info = requests.get(snp_url, headers=self.headers).json()
            ensemble_url = 'https://rest.ensembl.org/variation/human/{}?content-type=application/json'.format(snp)
            ensemble_data = requests.get(ensemble_url).json()
            try:
                doc['chr'] = int(snp_info['locations'][0]['chromosomeName'])
                doc['chr_pos'] = int(snp_info['locations'][0]['chromosomePosition'])
                doc['region'] = snp_info['locations'][0]['region']['name']
                doc['functional_class'] = snp_info['functionalClass']
                doc['snp_name'] = snp
                doc['MAF'] = ensemble_data['MAF']
                doc['most_severe_consequence'] = ensemble_data['most_severe_consequence']
                doc['minor_allele'] = ensemble_data['minor_allele']
                doc['allele_string'] = ensemble_data['mappings'][0]['allele_string']
                doc['strand'] = ensemble_data['mappings'][0]['strand']
                doc['location'] = ensemble_data['mappings'][0]['location']
                doc['values'] = ensemble_data['mappings'][0]['allele_string'].split('/')
                genes = []
                for item in snp_info['genomicContexts']:
                    if item['source'] == 'NCBI':
                        genes.append(item['gene']['geneName'])
                doc['genes'] = genes
                ret.append(doc)
            except Exception as e:
                print(e)
                pass
        return ret

    def divide_snp_data(self, n):
        it = iter(self.snp_data)
        for i in range(0, len(self.snp_data), n):
            yield {k:self.snp_data[k] for k in islice(it, n)}

    def pull_snp_data_proc(self, n):
        smaller = list(self.divide_snp_data(n))
        start = timer()
        with Pool() as pool:
            res = pool.map(self.pull_snp_data, smaller)
        end = timer()
        print(f'elapsed time: {end - start}')
        gene_list = []
        for i in res:
            for a in i:
                for gene in a['genes']:
                    gene_list.append(gene)
        gene_list = set(gene_list)
        for item in gene_list:
            print(item)

# d = SNPDaemon('genes.json')
# d.pull_snp_data_proc(10)

d = GeneDaemon('gene_id_list.txt')
# d.load_gene_data()
# d.download_dataset('gene_id_list.txt')
d.get_gene_data_job(10)
# d.pull_gene_ids(10)
# d.download_dataset('gene_id_list.txt')