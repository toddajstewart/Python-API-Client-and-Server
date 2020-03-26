from flask import Flask #, request, jsonify, url_for
import os, re, csv
from colorama import init, Fore, Back, Style
init()

os.system('cls')

# endpoints list
#endpoints = ['countries','users']
#endpoints = []

###############################################################################
# get Dict keys as a List of unique keys (duplicates removed if they exist)
def getReducedKeysList(Dict):
    RKL = []
    for key in Dict.keys(): 
        RKL.append(key) 
    return RKL

files = ["countries.csv","users.csv"]

global endpoints
endpoints = []
global D
D = {}

###############################################################################
# read all files into dict D with filename as endpt and list file contents as values
def readFilesIntoDictList(files):
    #D = {}
    #endpoints = []
    # read each file
    for f in range(len(files)):
        # get endpt value from file name
        endpt = files[f].split('.')[0]
        endpoints.append(endpt)

        # open and read file into list of dicts DL
        csvFile = open(files[f],"r")
        line = ""
        DL = []
        for line in csv.DictReader(csvFile):        
            DL.append(line)

        # create dict with endpt as key and list DL as value
        D[endpt] = DL
    return D, endpoints

###############################################################################
# extract non-reduced list of keys from request string (can contain duplicate keys)
def getNonReducedKeysList(request):
    req = re.search(r"(?<=\?).*?(?=\')", str(request)).group(0) # get value between ? and '
    RPL = re.split("[&=]", req) # split string into request params list on either & or = characters
    NRKL = []
    for i in range(0, len(RPL), 2): # make new list of every odd list value
        NRKL.append(RPL[i])
    return NRKL

###############################################################################
# check request param keys are unique and subset of countries keys
#def subsetOf(request, endpoint):
def subsetOf(request, EPL):
    RKL = getReducedKeysList(request.args)
    NRKL = getNonReducedKeysList(request)

    if len(NRKL) != len(set(RKL)): # check param keys unique
        result = False        
    else:
        result = all(x in EPL for x in RKL) # check request param keys are subset of countries keys
    return result

###############################################################################
# get actual request part of the Flask requst string
def getRequest(request):
    req = re.search(r"(?<=\').*?(?=\')", str(request)).group(0) # get value between ' and '
    return req

###############################################################################
# get request endpoint
def getRequestEndPoint(request):
    #req = re.search(r"(?<=\').*?(?=\')", str(request)).group(0) # get value between ' and '
    req = getRequest(request)

    # try 3 re.search on req for 1) endpt, 2) ? param, 3) & params
    E = re.search(r"http://127\.0\.0\.1:5000/[A-Za-z0-9\_]+", req)
    Q = re.search(r"\?[A-Za-z0-9\_]+=[A-Za-z0-9\_]+", req)

    # get endpoint
    ES = req.rfind("/") + 1
    EE = len(req) if Q is None else req.find("?") # get last char index of endpoint
    endpoint = req[ES:EE]
    return endpoint

###############################################################################
# check that the request contains a valid endpoint
def validateEndpoint(request, endpoints):
    endpoint = getRequestEndPoint(request)
    result = False if endpoint not in endpoints else True # bad endpoint     
    return result

###############################################################################
# check for individual key value match
def matches(LK, rk, LV, rv):
    return 1 if LK == rk and LV == rv else 0    

###############################################################################
# get list of key value matches between LIST and REQUESTS
def matchKeysValuesInDictLists(request, LIST):
    GL = rk = rv = []
    #print(LIST)

    # get list of request keys and values
    for r in request: 
        rk = list(r.keys()) # get list of request keys
        rv = list(r.values()) # get list of request values

    # cycle thru list getting each item 
    for L in LIST:
        trueCount = 0        
        # get list item keys and values 
        for LK,LV in L.items():               
            # check list item keys and values against request keys and values
            for i in range(len(rk)):
                trueCount += matches(LK, rk[i], LV, rv[i])
            # if matches equal specified request key values, then add to get list
            if trueCount == len(rk):                
                GL.append(L)

    # remove list duplicates if any and return list
    GL = [i for n, i in enumerate(GL) if i not in GL[n + 1:]]  
    return GL

###############################################################################
# request methods
class Methods:
    # GET (view/query)
    def get(self, request, endpoint):               
        print("hello")
        endpoints = D.keys() 
        print("$$$$$$$$$$$$$$$$$$$$$$")
        match = validateEndpoint(request, endpoints)
        if match == False:
            return "Bad Request", 400
        else:    
            TL = D[endpoint]
            print(TL)
            print("+++++++++++++++++++++++")

            if len(request.args) == 0:
                return jsonify(LIST), 200
            #elif subsetOf(request, LIST) == True:
            elif subsetOf(request, endpoints) == True:
                #GL = [] # the get list               
                #RKL = getReducedKeysList(request.args) # never used ?!?

                GL = matchKeysValuesInDictLists(getRequest(request), LIST)
                print(GL)
                """
                for i in range(len(countries)): 
                    if ((countries[i]['name'] == request.args.get('name') or request.args.get('name') == None)
                    and (countries[i]['code'] == request.args.get('code') or request.args.get('code') == None)
                    and (countries[i]['capital'] == request.args.get('capital') or request.args.get('capital') == None)):
                        GL.append(countries[i])
                """    
                if len(GL) >= 1:
                    #GL = [i for n, i in enumerate(GL) if i not in GL[n + 1:]]  # remove duplicates                
                    return jsonify(GL), 200
                else:                 
                    print("A")
                    return "Not Found", 404
            else:
                print("B")
                return "Not Found", 404

    # POST (create/add record) - all fields need to be specified for a complete record to be created
    def post(self, request, countries):  
        match = validateEndpoint(request, endpoints)        
        if match == False:
            return "Bad Request", 400
        else:    
            if len(request.args) == 0:
                return "Bad Request", 400
            elif len(request.args) == P:
                found = False
                added = ""
                for i in range(len(countries)): 
                    if (countries[i]['name'] == request.args.get('name') 
                    and countries[i]['code'] == request.args.get('code')					  
                    and countries[i]['capital'] == request.args.get('capital')):
                        found = True
                        break
                if found == True:
                    return "Unauthorized", 401
                else:
                    countries.append(request.args)		
                    countries = sorted(countries, key = lambda i : i['name'])	  
                    return "Created", 201
            else:
                return "Bad Request", 400

    # DELETE
    def delete(self, request, countries):
        match = validateEndpoint(request, endpoints)
        if match == False:
            return "Bad Request", 400
        else:    
            if len(request.args) == 0:
                return "Unauthorized", 401
            else:
                found = False
                for i in range(len(countries)): 
                    if (countries[i]['name'] == request.args.get('name') 
                    or countries[i]['code'] == request.args.get('code')					  
                    or countries[i]['capital'] == request.args.get('capital')):
                        found = True
                        break
                if found == True:
                    countries.pop(i)
                    return "OK", 200
                else:
                    return "Not found", 404

    # PUT (update - all fields specified)
    def put(self, request, countries):
        match = validateEndpoint(request, endpoints)        
        if match == False:
            return "Bad Request", 400
        else:    
            if len(request.args) < len(EPL):
                return "Bad Request", 400
            elif subsetOf(request, countries) == True:
                found = False
                for i in range(len(countries)): 
                    if (countries[i]['name'] == request.args.get('name') 
                    or countries[i]['code'] == request.args.get('code')					  
                    or countries[i]['capital'] == request.args.get('capital')):
                        found = True
                        break
                if found == True:
                    countries[i]['name'] == request.args.get('name') 
                    countries[i]['code'] == request.args.get('code')					  
                    countries[i]['capital'] == request.args.get('capital')
                    return "OK", 200
                else:
                    return "Not found", 404

    # PATCH (update - not all fields specified)
    def patch(self, request, countries):       
        match = validateEndpoint(request, endpoints)       
        if match == False:
            return "Bad Request", 400
        else:  
            if len(request.args) < 2 or len(request.args) > len(EPL):
                return "Bad Request", 400
            elif subsetOf(request, countries) == True:
                count = 0
                for i in range(len(countries)): 
                    if (countries[i]['name'] == request.args.get('name') 
                    or countries[i]['code'] == request.args.get('code')					  
                    or countries[i]['capital'] == request.args.get('capital')):
                        countries[i]['name'] == request.args.get('name') 
                        countries[i]['code'] == request.args.get('code')					  
                        countries[i]['capital'] == request.args.get('capital')
                        count += 1
                if count > 0:
                    return "OK", 200
                else:
                    return "Not found", 404

    # OPTIONS (show supported request methods)
    def options(self, request):   
        match = validateEndpoint(request, endpoints)        
        if match == False:
            return "Bad Request", 400
        else:   
            if len(request.args) == 0:
                return str(methods),204
            else:
                return "Bad Request!", 400

    # HEAD (like GET, but with no content)
    def head(self, request, countries):
        match = validateEndpoint(request, endpoints)        
        if match == False:
            return "Bad Request", 400
        else:  
            if len(request.args) == 0:
                return "OK", 200
            elif subsetOf(request, countries) == True:
                GL = [] # the get list
                for i in range(len(countries)): 
                    if (countries[i]['name'] == request.args.get('name') 
                    or countries[i]['code'] == request.args.get('code')					  
                    or countries[i]['capital'] == request.args.get('capital')):
                        GL.append(countries[i])
                if len(GL) >= 1:
                    return "OK", 200
                else:                 
                    return "Not Found", 404

###############################################################################
# print server header blurb
def printHeader(methods):
    title = "*********************** API Test Server - T. Stewart, 2020 *********************"
    print(Style.RESET_ALL + Fore.YELLOW + Style.BRIGHT + title)
    print("Supported methods : " + str(methods))
    print(Style.RESET_ALL + '', end="")
    print("-" * 80)

# start doing stuff
methods = ['GET','POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH'] # supported request methods
printHeader(methods)
D, endpoints = readFilesIntoDictList(files)
api = Flask(__name__)

"""
# function apparently required to bind endpoints in following for loop to ???
def routeBinder():
    return ""
for endpoint in endpoints:
    api.add_url_rule("/" + endpoint, methods=methods, view_func=routeBinder)
"""

"""
def routeBinder():
    return ""
for endpoint in endpoints:
    api.route(endpoint, methods=methods, view_func=routeBinder)
"""

@api.route('/countries', methods=methods)
@api.route('/users', methods=methods)
###############################################################################
# all methods
def all_methods():          
    if request.method == 'GET':        
        print("buenos nachos!")
        endpoint = getRequestEndPoint(request)
        return Methods().get(request, endpoint)
    elif request.method == 'POST':
        endpoint = getRequestEndPoint(request)
        return Methods().post(request, endpoint)
    elif request.method == 'PUT':
        endpoint = getRequestEndPoint(request)
        return Methods().put(request, endpoint)
    elif request.method == 'DELETE':
        endpoint = getRequestEndPoint(request)
        return Methods().delete(request, endpoint)
    elif request.method == 'HEAD':
        endpoint = getRequestEndPoint(request)
        return Methods().head(request, endpoint)
    elif request.method == 'OPTIONS':
        endpoint = getRequestEndPoint(request)
        return Methods().options(request)
    elif request.method == 'PATCH':
        endpoint = getRequestEndPoint(request)
        return Methods().patch(request, endpoint)

# run server
if __name__ == '__main__':
    api.run()
    #api.run(debug=True)