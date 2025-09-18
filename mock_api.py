import pandas as pd

def verifyAadharDetails(aadhar_number):
    data = pd.read_csv('synthetic_aadhar_data.csv')

    email = data[data['UID'] == aadhar_number]['Email']

    # Add Logic for Sending OTP using SMTP 

    if email.empty:
        return False
    else:
        return True

def fetch_data(aadhar_number):
    data = pd.read_csv('synthetic_aadhar_data.csv')

    return data[data['UID'] == aadhar_number]


# aadhar_number = float(input("Enter Your Aadhar Number - ")) 

# if verifyAadharDetails(aadhar_number):
#     print(fetch_data(aadhar_number)) 
# else:
#     print("Invalid Aadhar Number or Detials Entered") 