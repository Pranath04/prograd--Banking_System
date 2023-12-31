import mysql.connector as mysql
from flask import Flask, request, jsonify, render_template
import uuid
import json
import re
from datetime import datetime

app = Flask(__name__)

db = mysql.connect(
    host = "localhost",
    user = "root",
    passwd = "root",
    database = "banking_application"
)

print(db)
cursor = db.cursor(buffered=True)

#creating user_details table
cursor.execute("CREATE TABLE IF NOT EXISTS user_details (id INT AUTO_INCREMENT PRIMARY KEY, first_name VARCHAR(255) NOT NULL, last_name VARCHAR(255) NOT NULL,phone_number char(10) NOT NULL,address text NOT NULL,date_of_birth  DATE NOT NULL,gmail varchar(40),aadhar_number char(12) NOT NULL,account_number char(16) NOT NULL,balance INT DEFAULT 0, UNIQUE (account_number) )")

#created Account number
def getAccountNumber():
    return str(uuid.uuid4().int)[:16]
    
#validating date of birth
def validate_date_format(date_string, date_format='%Y-%m-%d'):
    try:
        date_object=datetime.strptime(date_string, date_format)
        if date_object > datetime.now():
            return False
        return True
    except ValueError:
        return False

#updating balance
def updateBalance(account_number,balance, isDeposit):
    update_balance_query=f"UPDATE user_details SET balance = {balance} WHERE account_number = {account_number}"
    print(f"updateBalance : {update_balance_query}")
    try:
        cursor.execute(update_balance_query)
        db.commit()
        if(isDeposit):
            return jsonify({'success': 'Deposit successfully'}), 200
        else:
            return jsonify({'success': 'Withdraw successfully'}), 200  
    except Exception as e:
        return jsonify({'error': str(e)}),500


@app.route('/create_account', methods=['POST'])
def create_account():
    data = request.get_json()
    
    # Validate required fields
    if 'first_name' not in data or 'last_name' not in data or 'phone_number' not in data or 'address' not in data or 'aadhar_number' not in data or 'date_of_birth' not in data:
        return jsonify({"error": "Expected keys are first_name, last_name, phone_number, address, aadhar_number, date_of_birth"})

    # Validation for individual columns
    if(((data['first_name'].replace(' ', '')).isalpha() == False) ):
        return jsonify({"error":"First name accepts only characters"})
    if(((data['last_name'].replace(' ', '')).isalpha() == False)):
        return jsonify({"error":"Last name accepts only characters"})
    if((str(data['phone_number']).isdigit()==False)):
        return jsonify({"error":"Phone number accepts only digits"})
    if(len(str(data['phone_number']))!=10):
        return jsonify({"error":"Phone number should consist 10 digits"})
    if((str(data['aadhar_number']).isdigit()==False)  ):
        return jsonify({"error":"Aadhar number accepts only digits"})
    if(len(str(data['aadhar_number']))!=12):
        return jsonify({"error":"Aadhar number should consist 12 digits"})
    if((len(data['gmail'])<=10) or  ((((data['gmail'])[-10:]).lower())  != "@gmail.com")):
        return jsonify({"error":"Invalid gmail"})
    if (validate_date_format(data['date_of_birth']))==False:
        return jsonify({"error":"Invalid date of birth plese check formate YYYY-MM-DD"})

    
    aadhar_number_int = int(data['aadhar_number'])   

    # Duplicate User
    duplicate_user_check_query = f"select * from user_details where aadhar_number =  {aadhar_number_int} limit 1"
    print(f"Create_account : {duplicate_user_check_query}")
    cursor.execute(duplicate_user_check_query)
    duplicate_user_check = cursor.fetchall()
    if(len(duplicate_user_check) > 0):
       return jsonify({"error": "Aadhar Number already exists"}) 

    account_number = getAccountNumber()
    account_number_int = int(account_number)
    
    if 'gmail' not in data:
        insert_user_details_query = f"insert into user_details (first_name, last_name, phone_number, address, date_of_birth, aadhar_number, account_number) values ('{data['first_name']}', '{data['last_name']}', {int(data['phone_number'])}, '{data['address']}', '{data['date_of_birth']}', {aadhar_number_int}, {account_number_int}) "   
    else:
        insert_user_details_query = f"insert into user_details (first_name, last_name, phone_number, address, date_of_birth, gmail, aadhar_number, account_number) values ('{data['first_name']}', '{data['last_name']}', {int(data['phone_number'])}, '{data['address']}', '{data['date_of_birth']}', '{data['gmail']}',{aadhar_number_int}, {account_number_int}) " 
    
    print(f"Create_account : {insert_user_details_query}")

    try:
        cursor.execute(insert_user_details_query)
        db.commit()
        return jsonify({'success': f'Account was created successfully.Your account number is {account_number} '}), 200
    except Exception as e:
        return jsonify({'error': str(e)}),500

#deposit
@app.route('/deposit', methods=['PUT'])
def deposit():
    data = request.get_json()

    #validation
    if 'account_number' not in data or 'deposit_amount' not in data:
        return jsonify({"error": "Expected keys are account_number,deposit_amount"})
    if((str(data['account_number']).isdigit())==False):
        return jsonify({"error":"Account number accepts only digits"})
    if (len(str(data['account_number'])) != 16):
        return jsonify({"error":"Account number should consists 16 digits"})
    if((str(data['deposit_amount']).isdigit())==False):
        return jsonify({"error":"Deposit amount accepts only digits"})
    if(data['deposit_amount']<=0):
        return jsonify({"error":"Deposit should be grater than 0"})
    
    balance_query = f"select balance from user_details where account_number =  {data['account_number']}"
    print(f"deposit : {balance_query}")
    try:
        cursor.execute(balance_query)
        balance=cursor.fetchone()
        if balance is None:
            return jsonify({"error":"Invalid Account number,Please try again."})
        else:
            print(f"Before deposit- {data['account_number']}:{balance[0]}")
            updated_balance=int(balance[0])+int(data['deposit_amount'])
            print(f"deposit calculations- {data['account_number']}:{updated_balance}")
            return updateBalance(data['account_number'],updated_balance,True)
    except Exception as e:
        return jsonify({'error': str(e)}),500

#withdrawing
@app.route('/withdrawing', methods=['PUT'])
def withdrawing():
    data = request.get_json()
    #validation
    if 'account_number' not in data or 'withdraw_amount' not in data:
        return jsonify({"error": "Expected keys are account_number,withdraw_amount"})
    if((str(data['account_number']).isdigit())==False):
        return jsonify({"error":"Account number accepts only digits"})
    if (len(str(data['account_number'])) != 16):
        return jsonify({"error":"Account number should consists 16 digits"})
    if((str(data['withdraw_amount']).isdigit())==False):
        return jsonify({"error":"Withdraw amount accepts only digits"})
    if(data['withdraw_amount']<=0):
        return jsonify({"error":"Withdraw should be grater than 0"})
    
    balance_query = f"select balance from user_details where account_number =  {data['account_number']}"
    print(f"withdrawing : {balance_query}")
    try:
        cursor.execute(balance_query)
        balance=cursor.fetchone()
        if balance is None:
            return jsonify({"error":"Invalid Account number,Please try again."})

        if((int(balance[0])- int(data['withdraw_amount'])) < 0):
                return jsonify({"error":"Insufficent Balance"})    
        else:
            print(f"Before Withdraw- {data['account_number']}:{balance[0]}")
            updated_balance=int(balance[0])-int(data['withdraw_amount'])
            print(f"Withdraw calculations- {data['account_number']}:{updated_balance}")
            return updateBalance(data['account_number'],updated_balance,False)
    except Exception as e:
        return jsonify({'error': str(e)}),500

#balance
@app.route('/balance/<account_number>', methods=['GET'])
def balance(account_number):
    if((str(account_number).isdigit())==False):
        return jsonify({"error":"Account number accepts only digits"})
    if (len(str(account_number)) != 16):
        return jsonify({"error":"Account number should consists 16 digits"})

    balance_query = f"select balance from user_details where account_number =  {account_number}"
    try:
        cursor.execute(balance_query)
        balance=cursor.fetchone()
        if balance is None:
            return jsonify({"error":"Invalid Account number,Please try again."})
        else:
            return jsonify({"balance" : balance[0]})
    except Exception as e:
        return jsonify({'error': str(e)}),500

if __name__ == '__main__':
    app.run(debug=True)