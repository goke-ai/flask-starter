import os
from flask import current_app, flash, json, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
import pandas as pd

from app import db
from ..email import send_email

from ..models import User

from . import api


@api.route('/db', methods=['GET'])
def db():
    # Specify the path to your JSON file
    json_file_path = url_for('static', filename='db.json')
    json_file_path = os.path.join(current_app.static_folder, 'db.json')

    data = {}

    try:
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)
            # Now 'data' contains the contents of your JSON file as a Python dictionary
            print("JSON data loaded successfully!")
            # print(data)
    except FileNotFoundError:
        print(f"File '{json_file_path}' not found. Please check the file path.")
    except json.JSONDecodeError:
        print(
            f"Error decoding JSON data from '{json_file_path}'. Make sure the file contains valid JSON.")

    return data


@api.route('/students', methods=['GET'])
def students():
    df = pd.DataFrame({
        'id': ['S001', 'S002', 'S003'],
        'name': ['John Doe', 'Jane Smith', 'Emily Johnson'],
        'math': ['A', 'B', 'C'],
        'science': ['B', 'A', 'B'],
        'history': ['A', 'B', 'C'],
        'english': ['A', 'A', 'B']
    }).set_index('id')

    return df.to_dict()


@api.route('/banks', methods=['GET'])
# @login_required
def banks():
    banksJson = {
        "bank": {
            "name": "Sample Bank",
            "location": "123 Main Street, Anytown, AT 12345",
            "accounts": [
                {
                    "account_id": "001",
                    "account_type": "Checking",
                    "balance": 1500.75,
                    "currency": "USD",
                    "customer_id": "C001"
                },
                {
                    "account_id": "002",
                    "account_type": "Savings",
                    "balance": 5500.00,
                    "currency": "USD",
                    "customer_id": "C002"
                },
                {
                    "account_id": "003",
                    "account_type": "Business",
                    "balance": 25000.00,
                    "currency": "USD",
                    "customer_id": "C003"
                }
            ],
            "customers": [
                {
                    "customer_id": "C001",
                    "name": "John Smith",
                    "address": "101 First Street, Anytown, AT 12345"
                },
                {
                    "customer_id": "C002",
                    "name": "Jane Doe",
                    "address": "202 Second Street, Anytown, AT 12345"
                },
                {
                    "customer_id": "C003",
                    "name": "XYZ Corp.",
                    "address": "303 Third Street, Business District, Anytown, AT 12345"
                }
            ]
        }
    }

    return jsonify(banksJson)
