import json

from pymongo.errors import ServerSelectionTimeoutError

from webapp.view_helpers import get_mongo
from multiprocessing import Pool
from itertools import islice
import requests


class SNPDaemon:
    trait_id = "MONDO_0004975"
    headers = {'Accept': 'application/json'}
    data = None
    snps = []
    snp_data = {}
    sample_doc = {
        'chr': None,
        'chr_pos': None,
        'region': None,
        'functional_class': None,
        '_id': None,
        'MAF': None,
        'minor_allele': None,
        'most_severe_consequence': None,
        'location': None,
        'values': None,
        'genes': [],
        'strongest_risk_alleles': None,
        'is_intergenic': True,
        'risk_level': None,
        'p-value': None
    }

    risk_levels = {
         'intron_variant': 'MODIFIER', 'intergenic_variant': 'MODIFIER', 'non_coding_transcript_exon_variant': 'MODIFIER',
         'regulatory_region_variant': 'MODIFIER', 'missense_variant': 'MODERATE', '5_prime_UTR_variant': 'MODIFIER', '3_prime_UTR_variant': 'MODIFIER',
         'synonymous_variant': 'LOW', 'TF_binding_site_variant': 'MODIFIER', 'splice_donor_variant': 'HIGH', 'inframe_insertion': 'MODERATE',
         'splice_region_variant': 'LOW', 'stop_gained': 'HIGH', 'upstream_gene_variant': 'MODIFIER', 'downstream_gene_variant': 'MODIFIER', None: None
    }

    def __init__(self, *args):
        if len(args) > 0:
            f = args[0]
            f = open(f, 'r')
            try:
                self.data = json.load(f)
                f.close()
            except:
                exit()
        else:
            url = 'https://www.ebi.ac.uk/gwas/rest/api/efoTraits/{}'.format(self.trait_id)
            req = requests.get(url, headers=self.headers).json()
            url = req['_links']['associationsByTraitSummary']['href']

            # since pulling data from this url takes over 3 min, sometimes
            # it is easier to store the gene data in a json file once
            # and then load from there, since the request takes so long
            self.data = requests.get(url, headers=self.headers).json()
            f = open('snp_data.json', 'w')
            f.write(json.dumps(self.data))
            f.close()
        self.get_snps()

    def get_snps(self):
        associations = self.data['_embedded']['associations']
        for association in associations:
            for snp in association['snps']:
                doc = self.sample_doc.copy()
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
                doc['pvalue'] = association['pvalue']
                if snp['rsId'] in self.snp_data:
                    for item in doc['strongest_risk_alleles']:
                        if item not in self.snp_data[snp['rsId']]['strongest_risk_alleles']:
                            self.snp_data[snp['rsId']]['strongest_risk_alleles'] += doc['strongest_risk_alleles']
                self.snp_data[snp['rsId']] = doc

    def pull_snps(self, l):
        docs = []
        for snp in l:
            doc = {snp: self.snp_data[snp].copy()}
            snp_url = 'https://www.ebi.ac.uk/gwas/rest/api/singleNucleotidePolymorphisms/{}'.format(snp)
            snp_info = requests.get(snp_url, headers=self.headers).json()
            ensemble_url = 'https://rest.ensembl.org/variation/human/{}?content-type=application/json'.format(snp)
            ensemble_data = requests.get(ensemble_url).json()
            doc = self.new_snp_data(snp, snp_info, ensemble_data, doc[snp])
            self.update_mongo_doc(doc)
            docs.append(doc)
        return docs

    def update_mongo_doc(self, new_data):
        #update only if fields are new/different from mongo record
        #if no record, inserts new doc
        upsert = True
        conn = get_mongo()
        doc = conn.AdNet.SNPs.find_one({'_id': new_data['_id']})
        if doc:
            upsert = False
        try:

            conn.AdNet.SNPs.find_one_and_update(
                {'_id': new_data['_id'],
                '$or': [
                    {'chr': {'$ne': new_data['chr']}},
                    {'chr_pos': {'$ne': new_data['chr_pos']}},
                    {'region': {'$ne': new_data['region']}},
                    {'functional_class': {'$ne': new_data['functional_class']}},
                    {'MAF': {'$ne': new_data['MAF']}},
                    {'most_severe_consequence': {'$ne': new_data['most_severe_consequence']}},
                    {'minor_allele': {'$ne': new_data['minor_allele']}},
                    {'location': {'$ne': new_data['location']}},
                    {'values': {'$ne': new_data['values']}},
                    {'strongest_risk_alleles': {'$ne': new_data['strongest_risk_alleles']}},
                    {'genes': {'$ne': new_data['genes']}},
                    {'is_intergenic': {'$ne': new_data['is_intergenic']}},
                    {'risk_level': {'$ne': new_data['risk_level']}},
                    {'pvalue': {'$ne': new_data['pvalue']}}
                ]},
                {'$set': {
                    'chr': new_data['chr'],
                    'chr_pos': new_data['chr_pos'],
                    'region': new_data['region'],
                    'functional_class': new_data['functional_class'],
                    'MAF': new_data['MAF'],
                    'most_severe_consequence': new_data['most_severe_consequence'],
                    'minor_allele': new_data['minor_allele'],
                    'location': new_data['location'],
                    'values': new_data['values'],
                    'strongest_risk_alleles': new_data['strongest_risk_alleles'],
                    'genes': new_data['genes'],
                    'is_intergenic': new_data['is_intergenic'],
                    'risk_level': new_data['risk_level'],
                    'pvalue': new_data['pvalue']
                }}, upsert=upsert
            )
        except ServerSelectionTimeoutError as e:
            print("What")
        except Exception as f:
            print("confused")




    def new_snp_data(self, snp, snp_info, ensemble_info, doc):
        try:
            if snp_info['locations'] != []:
                doc['chr'] = snp_info['locations'][0]['chromosomeName']
                doc['chr_pos'] = snp_info['locations'][0]['chromosomePosition']
                doc['region'] = snp_info['locations'][0]['region']['name']
                doc['location'] = '{}:{}'.format(doc['chr'], doc['chr_pos'])
            doc['functional_class'] = snp_info['functionalClass']
            doc['_id'] = snp
            print(self.risk_levels[doc['functional_class']])
            print(doc['functional_class'])
            doc['risk_level'] = self.risk_levels[doc['functional_class']]
            if 'error' not in ensemble_info.keys():
                doc['MAF'] = ensemble_info['MAF']
                doc['minor_allele'] = ensemble_info['minor_allele']
                doc['most_severe_consequence'] = ensemble_info['most_severe_consequence']
                doc['values'] = ensemble_info['mappings'][0]['allele_string'].split('/')
                if doc['location'] == None:
                    doc['location'] = ensemble_info['mappings'][0]['location']
            genes = self.find_genes_by_snp(snp_info)
            if genes[0] == 0:
                doc['is_intergenic'] = False
            doc['genes'] = genes[1:]
        except Exception as e:
            print(e)
        return doc

    def find_genes_by_snp(self, snp_info):
        genes = [0]
        for item in snp_info['genomicContexts']:
            if not item['isIntergenic'] and item['source'] == 'Ensembl' and item['gene']['geneName'] not in genes:
                genes.append(item['gene']['geneName'])
        if len(genes) == 1:
            genes = self.find_closest_genes(snp_info)
        return genes

    def find_closest_genes(self, snp_info):
        genes = [1]
        for item in snp_info['genomicContexts']:
            if item['isIntergenic'] and item['source'] == 'Ensembl' and item['gene']['geneName'] not in genes:
                genes.append(item['gene']['geneName'])
        return genes

    def divide_snp_list(self, n):
        it = iter(self.snp_data)
        for i in range(0, len(self.snp_data), n):
            yield {k: self.snp_data[k] for k in islice(it, n)}

    def write_gene_ids(self, gene_list):
        upsert = True
        conn = get_mongo()
        for gene in gene_list:
            doc = conn.AdNet.GeneIds.find_one({'_id': gene})
            if not doc:
                upsert = False
            conn.AdNet.GeneIds.insert_one(
                {'_id': gene}
            )

    def pull_snp_data(self, n):
        #needs to be called outside of constructor since this is an expensive operation
        # even with multiprocessing
        smaller = list(self.divide_snp_list(n))
        with Pool() as pool:
            res = pool.map(self.pull_snps, smaller)

        #take the resultant gene_list and store it into a text file for checking later
        gene_list = []
        for i in res:
            for item in i:
                for gene in item['genes']:
                    gene_list.append(gene)
        gene_list = set(gene_list)
        self.write_gene_ids(gene_list)


s = SNPDaemon('snp_data.json')
s.pull_snp_data(10)