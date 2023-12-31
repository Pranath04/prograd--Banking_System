# prograd--Banking_System
 Banking System

**Before Execution:**
Please Update the db configuration ie., user_name (user) , password(passwd), database_name(database). Please check the sample source code here.
mysql.connect(
    host = "localhost",
    user = "root",
    passwd = "root",
    database = "banking_application"
)

=============================================================

**Execute the application**
python3 banking.py

=============================================================

**Test the application using postman:**

**1. Create Account**
   
   Method : POST
   URL : /create_account
   Body : 
        {
           "first_name":"Pranath",
           "last_name":"Meda",
           "phone_number":"9988776655",
           "address":"5-6,talu office street,podili,AP",
           "date_of_birth":"2002-07-20",
           "gmail":"medanarayanapranath@gmail.com",
           "aadhar_number":"987456321012"
         }
   
**2. Deposit Amount**

   Method : PUT
   URL : /deposit
   Body : 
       {
         "account_number":2018222169166870,
         "deposit_amount":500
       }
   
**3. Withdraw Amount**

   Method : PUT
   URL : /withdrawing
   Body : 
       {
         "account_number":2018222169166870,
         "withdraw_amount":500
       }
   
**4. Check Balance**

   Method : PUT
   URL : /balance/2372817253527043

**NOTE:** Send Body in JSON format for every request
