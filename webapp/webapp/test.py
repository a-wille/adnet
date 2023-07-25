from pymongo import MongoClient
from flask import Flask, request, jsonify
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.python.keras import layers
from natsort import natsorted
from threading import Thread


global data
location_class = {
	'intergenic_variant': '2',
	'regulatory_region_variant': '1',
	'TF_binding_site_variant': '1',
	'downstream_variant': '9',
	'upstream_variant': '2',
	'intron_variant': '6',
	'non_coding_transcript_exon_variant': '10',
	'3_prime_UTR_variant': '8',
	'5_prime_UTR_variant': '3',
	'synonymous_variant': '4',
	'splice_donor_variant': '5',
	'splice_region_variant': '6',
	'missense_variant': '4',
	'inframe_insertion': '4',
	'stop_gained': '4'
}
risk_level = {
	'HIGH': 4,
	'MODERATE': 3,
	'LOW': 2,
	'MODIFIER': 1
}


app = Flask(__name__)

# the minimal Flask application
@app.route('/')
def index():
    return '<h1>Hello, World!</h1>'

def find_indexes(concerned_snps, organized):
    conn = get_mongo()
    return_dict = {}
    for item in concerned_snps:
        doc = conn.AdNet.SNPs.find_one({'_id': item}, {'chr': 1, 'chr_pos': 1})
        locale = '{}:{}'.format(doc['chr'], doc['chr_pos'])
        index = organized.index(locale)
        return_dict[item] = index
    return return_dict


def get_organized_snps():
    conn = get_mongo()
    docs = list(conn.AdNet.SNPs.find({}, {'chr': 1, 'chr_pos': 1}))
    new_docs = []
    for doc in docs:
        new_docs.append('{}:{}'.format(doc['chr'], doc['chr_pos']))
    return natsorted(new_docs)


def get_mongo(**kwargs):
    # allows an instance of a mongo connection to allow for inserts, edits, and
    # deletes into the mongo database
    global _mongo_conn
    user = 'user'
    pw = 'securityismypassion'
    _mongo_conn = MongoClient("mongodb+srv://adnet.khzkajw.mongodb.net/AdNet", username=user, password=pw)
    return _mongo_conn


@app.route('/build/', methods=['POST'])
def submitting_job_function():
    print(request.json)
    daemon = Thread(target=build_model, args=(request.json,), daemon=True, name='model')
    daemon.start()
    return({'message': 'perhaps?'})




def build_model(data):
    print(data)
    print("start build")
    concerned_snps = []
    for i in ['one', 'two', 'three', 'four', 'five']:
        if data[i] != '':
            concerned_snps.append(data[i])
        organized = get_organized_snps()
        indexes = find_indexes(concerned_snps, organized)
        conn = get_mongo()
        genetic_docs = list(conn.AdNet.RiggedData.find({}, {'_id': 0, 'data': 1, 'outcome': 1}))
        final_data = []
        numeric_columns = []
        categorical_columns = []
        for doc in genetic_docs:
            doc_dict = {}
            concerned_index = 0
            for index in indexes:
                i = indexes[index]
                doc_dict['r{}_risk'.format(concerned_index)] = 0
                doc_dict['r{}_fc'.format(concerned_index)] = '0'
                doc_dict['r{}_lc'.format(concerned_index)] = '0'
                if 'r{}_risk'.format(concerned_index) not in numeric_columns:
                    numeric_columns.append('r{}_risk'.format(concerned_index))
                    categorical_columns.append('r{}_fc'.format(concerned_index))
                    categorical_columns.append('r{}_lc'.format(concerned_index))
                if doc['data'][i] == 1:
                    snp_data = conn.AdNet.SNPs.find_one({'_id': concerned_snps[concerned_index]})
                    risk = risk_level[snp_data['risk_level']]
                    f_class = snp_data['functional_class']
                    l_class = str(list(location_class.keys()).index(snp_data['functional_class']))
                    doc_dict['r{}_risk'.format(concerned_index)] = risk
                    doc_dict['r{}_fc'.format(concerned_index)] = f_class
                    doc_dict['r{}_lc'.format(concerned_index)] = l_class
                concerned_index += 1
            doc_dict['AD'] = 1
            if doc['outcome'] == 'Not AD':
                doc_dict['AD'] = 0
            final_data.append(doc_dict)
        df = pd.DataFrame.from_records(final_data)
        df.head()
        numerical_transformer = Pipeline(steps=[
		('scaler', StandardScaler())  # Standardize the numerical features
	])
        categorical_transformer = Pipeline(steps=[
		('onehot', OneHotEncoder())  # One-hot encode the categorical features
	])
        preprocessor = ColumnTransformer(transformers=[
		('num', numerical_transformer, numeric_columns),
		('cat', categorical_transformer, categorical_columns)
	])

	# Fit and transform the data
        processed_data = preprocessor.fit_transform(df)

	# Get the column names after one-hot encoding
        categorical_names = preprocessor.named_transformers_['cat'].named_steps['onehot'].get_feature_names_out(
		categorical_columns)

	# Convert the processed data back to a DataFrame
        classification_column = df['AD'].to_numpy()
        processed_df = pd.DataFrame(
		np.hstack((processed_data[:, :len(numeric_columns)], processed_data[:, len(numeric_columns):],
				   classification_column.reshape(-1, 1))),
		columns=numeric_columns + list(categorical_names) + ['AD']
	)
        processed_df.head()
        model = tf.keras.Sequential([
		layers.Dense(64, activation='relu', input_shape=(13,)),
		layers.Dense(64, activation='relu'),
		layers.Dense(1, activation='sigmoid')
	])
	# Compile the model
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        x = processed_df.drop('AD', axis=1)  # Input features, excluding the target column
        y = processed_df['AD']  # Target variable
        x_train, x_val, y_train, y_val = train_test_split(x, y, test_size=0.2, random_state=42)
        x_train, x_test, y_train, y_test = train_test_split(x_train, y_train, test_size=0.1, random_state=42)
        model.fit(x_train, y_train, epochs=10, batch_size=32, validation_data=(x_val, y_val))
        loss, accuracy = model.evaluate(x_test, y_test)
        print("end build")
        return jsonify({'message': 'it ran at least'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)