from logging import debug
from flask import Flask, request
import os
import psycopg2
import uuid
import json
from flask_cors import CORS

app = Flask(__name__)
# https://stackoverflow.com/a/64657739
CORS(app, support_credentials=True)
# https://devcenter.heroku.com/articles/heroku-postgresql#connecting-in-python

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
# https://stackoverflow.com/a/43634941
conn.autocommit = True

cursor = conn.cursor()
try:
    cursor.execute('''
        DROP TABLE IF EXISTS services;
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS services (
        service_id varchar(64) PRIMARY KEY,
        service_name varchar(256),
        service_description varchar(256),
        service_category varchar(256)
    );
    ''')
except psycopg2.Error:
    print('Error occurred while creating table')

@app.route('/health-check')
def health_check():
    return {'status': 200}

@app.route('/create-services', methods=['POST'])
def create_service():
    # https://stackoverflow.com/a/67461897
    data = request.get_json()
    service_id = str(uuid.uuid4())
    service_name = data['service_name']
    service_description = data['service_description']
    service_category = data['service_category']
    query = '''
        INSERT INTO services (service_id, service_name, service_description, service_category)
        VALUES (%s, %s, %s, %s)
    '''
    cursor.execute(query, [service_id, service_name, service_description, service_category])
    return {'status': 201, 'service_id': service_id}

@app.route('/get-service/<user_id>')
def get_service(user_id):
    query = '''
        SELECT service_id, service_name, service_description, service_category FROM services, users where users.user_id=%s
    '''
    cursor.execute(query, [str(user_id)])
    res = cursor.fetchall()
    if (len(res) == 0):
        return {'status': 200, 'service': None}
    service = {
        'service_id': res[0][0],
        'service_name': res[0][1],
        'service_description': res[0][2],
        'service_category': res[0][3]
    }
    return {'status': 200, 'service': service}

@app.route('/delete-service/<service_id>', methods=['DELETE'])
def delete_service(service_id):
    query = '''
        DELETE FROM services WHERE services.service_id=%s
    '''
    cursor.execute(query, [str(service_id)])
    return {'status': 200}

# https://www.youtube.com/watch?v=4eQqcfQIWXw
if __name__ == '__main__':
    port = os.environ.get('PORT', 5000)
    app.run(debug=True, host='0.0.0.0', port=port)