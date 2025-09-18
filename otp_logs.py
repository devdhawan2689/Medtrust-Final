import pandas as pd

def store_records(uid, otp):
    logs = pd.read_csv('otp_logs.csv')

    if logs[logs['UID'] == uid].empty:
        new_data = pd.DataFrame([[uid, otp]], columns=['UID','OTP'])

        print(new_data)

        print(logs)
        
        logs = pd.concat([new_data, logs])

        print(new_data)

        print(logs)
    else:
        return "OTP Already Generated"

    logs.to_csv('otp_logs.csv', index = False)

    return "Done"

def fetch_record(uid):
    logs = pd.read_csv('otp_logs.csv')
     
    print(logs[logs['UID'] == int(uid)]['OTP'])
    
    return logs[logs['UID'] == int(uid)]['OTP'] 

def delete_record(uid):
    logs = pd.read_csv('otp_logs.csv')

    logs = logs.drop(logs[logs['UID'] == uid]['UID'].index) 
    
    logs.to_csv('otp_logs.csv', index = False) 