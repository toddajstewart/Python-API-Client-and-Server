# Python-API-Client-and-Server
Description:
- Single endpoint (http://127.0.0.1/countries) API test server REST program written in Python 3.8 based on Flask.
- Supported Request methods are : GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS.
- GET request method has been improperly implemented to allow the following request to return all record data for information purposes:
  http://127.0.0.1/countries
- requests.csv data format is : request method,request url,expected returned http status code
- countries.csv contains 10 rows of data and the data format is : name,code,capital
- 2 usages are available as follows, but you must download the 4 files (API_Test_Server.py, API_Test_Client.py, countries.csv, requests.csv) to the same folder on your local machine to enable all run options.

Usage Option 1:
1) Open a command prompt window and execute 'py API_Test_Server.py',
2) Open another command prompt window and execute 'py API_Test_Client.py requests.csv',
3) 'API_Test_Client.py' program reads list of requests from 'requests.csv' file, validates syntax inside client and forwards valid requests to the 'API_Test_Server.py' program. 
4) 'API_Test_Server.py' returns HTTP status code and description and JSON data to client which is then displayed against expected test result on the console.

Usage Option 2:
1) Open a command prompt window and execute 'py API_Test_Server.py',
2) Open Postman or any other REST API client and send individual requests.
3) Client application (not 'API_Test_Client.py') validates request syntax and forwards valid requests to the 'API_Test_Server.py' program. 
4) 'API_Test_Server.py' returns HTTP status code to the client which displays returned HTTP status code, description and JSON data. 
