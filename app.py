from flask import Flask, render_template, request, session, redirect
import comorbidity_prediction as cm
import disease_mapper as dm
import gpt_comorbidity as gpt
import json
import time
import ast
import requests
import pandas as pd 
import mock_api as uidai
import generate_otp as go
import otp_logs as ol
import sqlite3
import dashboard_data as fdd

app = Flask(__name__)

@app.route('/')
def index():
    '''Returns Home Page'''
    return render_template('index.html')

# @app.route('/gpt')
# def gpt():
#     return render_template('gpt_comorbidites_page.html')
    
@app.route('/comorbidity_predict')
def comorbidity_predict():
    '''Calls the Neo4j DB to search for Comorbidities and Returns a DF of Top 20 Comorbidities'''
    disease = request.args.get('disease')

    mapped_disease = dm.mapper.map(disease)

    if mapped_disease['canonical_name'] != None:
        comorbidites = cm.comorbidities_of([mapped_disease['canonical_name']])

        print(type(comorbidites))

        print(comorbidites)

        # Convert to HTML with Bootstrap classes
        table_html = comorbidites.to_html(
            classes="table table-striped table-hover table-bordered table-sm",
            index=False,
            border=0,
            escape=False
        )
        return render_template('comorbidites_page.html', table_html=table_html)
        
    else:
        return "Invalid Disease Name Entered"

@app.route('/search_disease')
def search_disease():
    ''' Search Page that Allows User to search for Disease Comorbidity'''
    return render_template('search_disease.html')

@app.route('/comorb_predict', methods=['GET', 'POST'])
def comorb_predict():
    diseaseName = request.form['diseaseName']

    data = {'function': 'comorb_predict','query': diseaseName}

    data_json = json.dumps(data) 

    try:
        headers = {'Content-Type': 'application/json'}

        response = requests.post('http://medtrust.pythonanywhere.com/requestQuery', headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            data_found = False
            start_time = time.time() 
            end_time = start_time + 20 

            while time.time() < end_time:
                data = {'request_id': int(response.text)}

                output_response = requests.post('http://medtrust.pythonanywhere.com/getQueryOutput', headers=headers, data=json.dumps(data))

                data = ast.literal_eval(output_response.text)

                to_check = dict({'output': 'No Data Recieved Yet!'})
                print(data)
                print(type(data))
                print(to_check)
                print(type(to_check))

                if data != to_check:
                    data_found = True
                    break  

        if data_found == True:
            print(output_response.text)
            comorbidites = ast.literal_eval(output_response.text)
            comorbidites = pd.read_json(json.dumps(comorbidites), orient="records")

            # Convert to HTML with Bootstrap classes
            table_html = comorbidites.to_html(
            classes="table table-striped table-hover table-bordered table-sm",
            index=False,
            border=0,
            escape=False)

            return render_template('comorbidites_page.html', table_html=table_html)

        else:
            comorbidites = gpt.get_top_comorbidities(diseaseName)
            # Convert to HTML with Bootstrap classes
            table_html = comorbidites.to_html(
            classes="table table-striped table-hover table-bordered table-sm",
            index=False,
            border=0,
            escape=False)

            return render_template('gpt_comorbidites_page.html', table_html=table_html)
    except Exception as e:
        comorbidites = gpt.get_top_comorbidities(diseaseName)
        # Convert to HTML with Bootstrap classes
        table_html = comorbidites.to_html(
        classes="table table-striped table-hover table-bordered table-sm",
        index=False,
        border=0,
        escape=False)

        return render_template('gpt_comorbidites_page.html', table_html=table_html)

@app.route('/patient-login', methods=['GET', 'POST'])
def patient_login():
    return render_template('aadhaar_form.html')

@app.route('/hospital-login', methods=['GET', 'POST'])
def hospital_login():
    return render_template('aadhaar_form.html')

@app.route('/getOTP', methods=['GET', 'POST'])
def getOTP():
    aadhaar_number = int(request.form['aadhaar_number'])
    
    if uidai.verifyAadharDetails(aadhaar_number):
        otp = go.generate_otp()

        ol.store_records(aadhaar_number, otp)
        
        return render_template('otp_verification_with_alert.html', aadhaar_number = aadhaar_number, invalid_otp="false")
        # return str(uidai.fetch_data(aadhaar_number)) 
    else:
        return "Invalid Aadhar Number or Detials Entered" 

@app.route('/verify_otp', methods = ['GET', 'POST'])
def verify_otp():
    otp = int(request.form['otp'])
    uid = request.form['aadhaar_number']

    if int(ol.fetch_record(int(uid))) == otp:
        ol.delete_record(int(uid))

        return render_template('successfull_verification.html') 
    else:
        return render_template('otp_verification_with_alert.html', aadhaar_number = uid, invalid_otp = "true")

@app.route('/dashboard', methods=['GET', 'POST'])
def base():
    # uid_to_search = request.form['uid_to_search']
    df = fdd.fetch_patient_data(894036000000)

    subject_id = int(df['subject_id'].values[0])

    admissions_df = fdd.fetch_admissions_data(subject_id)

    icu_data = fdd.fetch_icustays_data(subject_id)

    return render_template('dashboard.html', full_name=df['Full Name'].values[0], gender=df['gender'].values[0], dob=df['dob'].values[0], subject_id=df['subject_id'].values[0], 
        last_admission = admissions_df['admittime'].values[0], admission_type=admissions_df['admission_type'].values[0], icu=icu_data['ICU'].values[0], los=int(icu_data['los'].values[0])) 

@app.route('/patient-dashboard', methods=['GET', 'POST'])
def patient_dashboard():
    return render_template('patient_dashboard.html')

@app.route('/encounters', methods=['GET', 'POST'])
def encounters():
    return render_template('encounters.html')

@app.route('/labs', methods=['GET', 'POST'])
def labs():
    return render_template('labs.html')

@app.route('/meds', methods=['GET', 'POST'])
def meds():
    return render_template('meds.html')

@app.route('/notes', methods=['GET', 'POST'])
def notes():
    return render_template('notes.html')

@app.route('/predictions', methods=['GET', 'POST'])
def predictions():
    return render_template('predictions.html')

@app.route('/problems', methods=['GET', 'POST'])
def problems():
    return render_template('problems.html')

if __name__ == '__main__':
    app.run(debug=True) 