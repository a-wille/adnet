import collections
import shutil

import requests
import json
from multiprocessing import Pool
from timeit import default_timer as timer
from itertools import islice
import os, sys, subprocess
import xmltodict
from Bio import SeqIO
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from config import MONGO_USER, MONGO_PASS, DATA_DIR


def get_mongo(**kwargs):
    # allows an instance of a mongo connection to allow for inserts, edits, and
    # deletes into the mongo database
    global _mongo_conn
    _mongo_conn = MongoClient("mongodb+srv://adnet.khzkajw.mongodb.net/AdNet", username=MONGO_USER, password=MONGO_PASS)
    return _mongo_conn



class GeneDaemon:
    api_key = "baf3baa6f018c25575f11632ceea1257e808"
    headers = {'Accept': 'application/json'}
    sample_gene_doc = {
        'id': None,
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
    gene_ids = []
    gene_docs = {}
    syns = {}
    feature_types = types = ['Signal', 'Peptide', 'Chain', 'Propeptide', 'Transit peptide', 'DNA binding',
                             'Motif', 'Lipidation', 'Modified residue', 'Non-standard reside', 'Cross-link',
                             'Glycosylation', 'Disulfide bond', 'Site', 'Helix', 'Turn', 'Beta strand',
                             'Region', 'Domain', 'Binding site', 'Active site', 'Motif']

    def __init__(self):
        """never init GeneDaemon without running SNP Daemon first to get list of genes"""
        os.chdir(DATA_DIR)
        self.read_in_names()
        self.convert_names_to_ids(10)
        self.download_dataset()
        self.get_syns_and_data(10)
        self.pull_gene_data_process(10)
        self.clean_data_files()


    def clean_data_files(self):
        shutil.rmtree(os.path.join(DATA_DIR, 'ncbi_dataset'))
        os.remove(os.path.join(DATA_DIR, 'ncbi_dataset.zip'))
        os.remove(os.path.join(DATA_DIR, 'gene_list.txt'))


    def read_in_names(self):
        conn = get_mongo()
        docs = conn.AdNet.GeneIds.find({})
        genes = []
        for doc in docs:
            genes.append(doc['_id'])
        self.genes = genes

    def divide_data(self, n):
        for i in range(0, len(self.gene_ids), n):
            yield self.gene_ids[i:i+n]

    def divide_name_data(self, n):
        for i in range(0, len(self.genes), n):
            yield self.genes[i:i+n]

    def pull_syn_data(self, data):
        to_ret = {}
        for gene in data:
            command = ['./datasets', 'summary', 'gene', 'symbol', '{}'.format(gene), '--taxon', '9606', '--as-json-lines']
            ps = subprocess.Popen(command, stdout=subprocess.PIPE)
            a = ps.communicate()[0].decode('utf-8').strip().split('\n')[0]
            output = {}
            if a != '':
                output = json.loads(a)
            try:
                num = int(output['gene_id'])
                if 'synonyms' in output.keys() and len(output['synonyms']) != 0:
                    to_ret[num] = output['synonyms']
            except KeyError as e:
                try:
                    if 'warnings' in output.keys() and output['warnings'][0]['gene_warning_code'] == 'UNRECOGNIZED_GENE_SYMBOL':
                        pass
                except KeyError as e:
                    print(e)
            except Exception as e:
                print(e)
        return to_ret

    def get_syns_and_data(self, n):
        smaller = list(self.divide_name_data(n))
        with Pool() as pool:
            res = pool.map(self.pull_syn_data, smaller)
        for item in res:
            for syn in item.keys():
                self.syns[syn] = item[syn]

    def convert_names_to_ids(self, n):
        smaller = list(self.divide_name_data(n))
        with Pool() as pool:
            res = pool.map(self.pull_id_data, smaller)
        gene_ids = []
        for l in res:
            gene_ids.extend(l)
        self.gene_ids = gene_ids

    def pull_id_data(self, data):
        gene_id_list = []
        for gene in data:
            command = ['./datasets', 'summary', 'gene', 'symbol', '{}'.format(gene), '--taxon', '9606', '--as-json-lines']
            ps = subprocess.Popen(command, stdout=subprocess.PIPE)
            process_output = ps.communicate()[0]
            if process_output and process_output != '':
                output = json.loads(process_output.decode('utf-8').strip().split('\n')[0])
            try:
                num = int(output['gene_id'])
                gene_id_list.append(num)
            except KeyError as e:
                try:
                    if 'warnings' in output:
                        if output['warnings'][0]['gene_warning_code'] == 'UNRECOGNIZED_GENE_SYMBOL':
                            print("ok")
                except KeyError as e:
                    print(e)
            except Exception as e:
                print(e)
        return gene_id_list


    def download_dataset(self):
        gene_str = ''
        for gene in self.gene_ids:
            gene_str += '{}\n'.format(gene)
        f = open('gene_list.txt', 'w')
        f.write(gene_str)
        f.close()
        base_command = './datasets download gene gene-id --inputfile {} && unzip -o ncbi_dataset.zip'
        command = base_command.format('gene_list.txt')
        x = subprocess.Popen(command, shell=True)
        x.wait()


    def pull_gene_data_process(self, n):
        self.gene_data = self.pull_json_data()
        self.rna_data = self.pull_rna_data()
        smaller = list(self.divide_data(n))
        with Pool() as pool:
            pool.map(self.pull_gene_data, smaller)


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
            try:
                g = self.gene_data[str(gene)]
                type = g['type']
            except Exception as e:
                type = ''
            try:
                doc['id'] = gene
                doc['_id'] = g['symbol']
                doc['description'] = g['description']
                doc['chromosome'] = g['chromosomes'][0]
                doc['expression'] = self.get_expression_vals(gene)
                doc['type'] = type
            except Exception as e:
                g = None
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
                doc['range']= g['annotations'][0]['genomicLocations'][0]['genomicRange']
            except:
                doc['range'] = {'begin': -1, 'end': -1, 'orientation': ""}
            if doc['type'] == 'PROTEIN_CODING':
                doc = self.try_protein_info(doc)
            try:
                doc = self.annotate_snp_data(doc)
                if doc['mod_len'] == 0 and doc['nm_len'] == 0:
                    g = None
            except Exception as e:
                g = None
            if g:
                self.update_mongo_doc(doc)

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
        doc['snp_effects'] = []
        conn = get_mongo()
        total_genes = [doc['_id']]
        if doc['id'] in self.syns.keys():
            total_genes += self.syns[doc['id']]
        for gene in total_genes:
            snps = conn.AdNet.SNPs.find({'genes': '{}'.format(gene)})
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
        try:
            content = json.loads(requests.get(url).content.decode('utf8'))
            num = self.find_correct_consequence(content['transcriptLevelConsequence'], snp)
            affected_features = []
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
        doc = conn.AdNet.Genes.find_one({'_id': new_data['_id']})
        if doc:
            upsert = False
        try:
            conn.AdNet.Genes.find_one_and_update(
                {'_id': new_data['_id'],
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
                    {'snp_effects': {'$ne': new_data['snp_effects']}},
                    {'mod_len':{'$ne': new_data['mod_len']}},
                    {'nm_len': {'$ne': new_data['nm_len']}},
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
                    'snp_effects': new_data['snp_effects'],
                    'mod_len': new_data['mod_len'],
                    'nm_len': new_data['nm_len']
                }}, upsert=upsert
            )
        except Exception as f:
            print(f)



class SNPDaemon:
    trait_id = "MONDO_0004975"
    headers = {'Accept': 'application/json'}
    data = None
    snps = []
    snp_data = {}
    genes = []
    docs = {}
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
        'pvalue': None
    }
    risk_levels = {
        'intron_variant': 'MODIFIER', 'intergenic_variant': 'MODIFIER',
        'non_coding_transcript_exon_variant': 'MODIFIER',
        'regulatory_region_variant': 'MODIFIER', 'missense_variant': 'MODERATE', '5_prime_UTR_variant': 'MODIFIER',
        '3_prime_UTR_variant': 'MODIFIER',
        'synonymous_variant': 'LOW', 'TF_binding_site_variant': 'MODIFIER', 'splice_donor_variant': 'HIGH',
        'inframe_insertion': 'MODERATE',
        'splice_region_variant': 'LOW', 'stop_gained': 'HIGH', 'upstream_gene_variant': 'MODIFIER',
        'downstream_gene_variant': 'MODIFIER', None: None
    }

    def __init__(self, num_proc):
        # pull associations with AD from EBI GWAS database
        url = 'https://www.ebi.ac.uk/gwas/rest/api/efoTraits/{}'.format(self.trait_id)
        req = requests.get(url, headers=self.headers).json()
        url = req['_links']['associationsByTraitSummary']['href']
        # pull GWAS SNP data for each snp associated with AD
        self.data = requests.get(url, headers=self.headers).json()
        self.get_snps()
        self.pull_snp_data_proc(num_proc)


    def get_snps(self):
        # updates self.snp_data dictionary with GWAS values (risk allele and probability) if found
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
                # sometimes double reported values from different experiments on an SNP so fuck that
                doc['strongest_risk_alleles'] = risk_list
                doc['pvalue'] = association['pvalue']
                if snp['rsId'] in self.snp_data:
                    for item in doc['strongest_risk_alleles']:
                        if item not in self.snp_data[snp['rsId']]['strongest_risk_alleles']:
                            self.snp_data[snp['rsId']]['strongest_risk_alleles'] += doc['strongest_risk_alleles']
                self.snp_data[snp['rsId']] = doc

    def update_mongo_doc(self, new_data):
        # update only if fields are new/different from mongo record
        # if no record, inserts new doc
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
                     {'pvalue': {'$ne': new_data['pvalue']}},
                     {'studies': {'$ne': new_data['studies']}}
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
                    'pvalue': new_data['pvalue'],
                    'studies': new_data['studies'],
                }}, upsert=upsert
            )
        except ServerSelectionTimeoutError as e:
            print("What")
        except Exception as f:
            print("confused")

    def pull_snp_data(self, data):
        # creates snp document using Ensembl and EBI GWAS databases. Please reference
        # sample document at the top of the class to see an example of document structure
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
                doc['_id'] = snp
                doc['MAF'] = ensemble_data['MAF']
                doc['most_severe_consequence'] = ensemble_data['most_severe_consequence']
                doc['minor_allele'] = ensemble_data['minor_allele']
                doc['allele_string'] = ensemble_data['mappings'][0]['allele_string']
                doc['strand'] = ensemble_data['mappings'][0]['strand']
                doc['location'] = ensemble_data['mappings'][0]['location']
                doc['values'] = ensemble_data['mappings'][0]['allele_string'].split('/')
                doc['risk_level'] = self.risk_levels[doc['functional_class']]
                doc['studies'] = snp_info['_links']['studies']
                genes = self.find_genes_by_snp(snp_info)
                doc['is_intergenic'] = True
                if genes[0] == 0:
                    doc['is_intergenic'] = False
                doc['genes'] = genes[1:]
                self.update_mongo_doc(doc)
                ret.append(doc)
            except Exception as e:
                print(e)
        return ret

    def find_closest_genes(self, snp_info):
        # find all genes that are related to the intergenic snp passed in
        genes = [1]
        for item in snp_info['genomicContexts']:
            if item['isIntergenic'] and item['gene']['geneName'] not in genes:
                genes.append(item['gene']['geneName'])
        return genes

    def find_genes_by_snp(self, snp_info):
        # returns a list of an int followed by string gene names
        # if 0 is returned first, then it is not an intergenic snp
        # if 1 is returned first, then it is an intergenic snp
        genes = [0]
        for item in snp_info['genomicContexts']:
            if not item['isIntergenic'] and item['isUpstream'] == False \
                    and item['isDownstream'] == False and item['gene']['geneName'] not in genes:
                # return gene(s)? (should just be one) where the non-intergenic SNP is located
                genes.append(item['gene']['geneName'])
        if len(genes) == 1:
            # function call to find all close genes and genomic contexts
            genes = self.find_closest_genes(snp_info)
        return genes

    def divide_snp_data(self, n):
        # divide snp list for threading purposes
        it = iter(self.snp_data)
        for i in range(0, len(self.snp_data), n):
            yield {k: self.snp_data[k] for k in islice(it, n)}

    def write_gene_ids(self, gene_list):
        # save list of related genes to mongo
        conn = get_mongo()
        full_list = list(conn.AdNet.GeneIds.find({}))
        for item in full_list:
            if item['_id'] not in gene_list:
                conn.AdNet.Genes.delete_one({'_id': item['_id']})
        conn.AdNet.GeneIds.delete_many({})
        for gene in gene_list:
            conn.AdNet.GeneIds.insert_one({'_id': gene})

    def pull_snp_data_proc(self, n):
        # implement threading for pulling snp data quicker
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
        self.write_gene_ids(gene_list)

# d = SNPDaemon(10)
d2 = GeneDaemon()

