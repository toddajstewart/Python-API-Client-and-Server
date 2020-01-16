from flask import Flask, request, jsonify
import csv
import requests
from os import system
from colorama import init, Fore, Back, Style
import re
init()
system('cls')

# supported request methods
methods = ['GET','POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH']

# endpoints list
endpoints = ['countries','users']

# get Dict keys as a List of unique keys (duplicates removed if they exist)
def getReducedKeysList(Dict):
    RKL = []
    for key in Dict.keys(): 
        RKL.append(key) 
    return RKL

# read CSV file into list of dicts
countries = []
EPL = [] # endpoint parameters list
csvFile = open("countries.csv","r")
line = ""
for line in csv.DictReader(csvFile):
    countries.append(line)
EPL = getReducedKeysList(line)
P = len(line)

# extract non-reduced list of keys from request string (can contain duplicate keys)
def getNonReducedKeysList(request):
    req = re.search(r"(?<=\?).*?(?=\')", str(request)).group(0) # get value between ? and '
    RPL = re.split("[&=]", req) # split string into request params list on either & or = characters
    NRKL = []
    for i in range(0, len(RPL), 2): # make new list of every odd list value
        NRKL.append(RPL[i])
    return NRKL

# check request param keys are unique and subset of countries keys
def subsetOf(request, countries):
    RKL = getReducedKeysList(request.args)
    NRKL = getNonReducedKeysList(request)

    if len(NRKL) != len(set(RKL)): # check param keys unique
        result = False        
    else:
        result = all(x in EPL for x in RKL) # check request param keys are subset of countries keys
    return result

# check that the request contains a valid endpoint
def validateEndpoint(request, EL):
    req = re.search(r"(?<=\').*?(?=\')", str(request)).group(0) # get value between ' and '

    # try 3 re.search on req for 1) endpt, 2) ? param, 3) & params
    E = re.search(r"http://127\.0\.0\.1:5000/[A-Za-z0-9\_]+", req)
    Q = re.search(r"\?[A-Za-z0-9\_]+=[A-Za-z0-9\_]+", req)

    # get endpoint
    ES = req.rfind("/") + 1
    EE = len(req) if Q is None else req.find("?") # get last char index of endpoint
    endpoint = req[ES:EE]
    result = False if endpoint not in EL else True # bad endpoint     
    return result

# check for individual key value match
def matches(LK, rk, LV, rv):
    return 1 if LK == rk and LV == rv else 0    

# get list of key value matches between LIST and REQUESTS
def matchKeysValuesInDictLists(REQS, LIST):
    GL = RK = RV = []

    # get list of request keys and values
    for R in REQS: 
        RK = list(R.keys()) # get list of request keys
        RV = list(R.values()) # get list of request values

    # cycle thru list getting each item 
    for L in LIST:
        trueCount = 0        
        # get list item keys and values 
        for LK,LV in L.items():               
            # check list item keys and values against request keys and values
            for i in range(len(RK)):
                trueCount += matches(LK, RK[i], LV, RV[i])
            # if matches equal specified request key values, then add to get list
            if trueCount == len(RK):                
                GL.append(L)

    # remove list duplicates if any and return list
    GL = [i for n, i in enumerate(GL) if i not in GL[n + 1:]]  
    return GL

# request methods
class Methods:
    # GET (view/query)
    def get(self, request, countries):       
        match = validateEndpoint(request, endpoints)
        if match == False:
            return "Bad Request", 400
        else:    
            if len(request.args) == 0:
                return jsonify(countries), 200
            elif subsetOf(request, countries) == True:
                GL = [] # the get list
                RKL = getReducedKeysList(request.args)

                #GL = matchKeysValuesInDictLists(REQS, LIST)

                for i in range(len(countries)): 
                    if ((countries[i]['name'] == request.args.get('name') or request.args.get('name') == None)
                    and (countries[i]['code'] == request.args.get('code') or request.args.get('code') == None)
                    and (countries[i]['capital'] == request.args.get('capital') or request.args.get('capital') == None)):
                        GL.append(countries[i])
                    
                if len(GL) >= 1:
                    GL = [i for n, i in enumerate(GL) if i not in GL[n + 1:]]  # remove duplicates
                    return jsonify(GL), 200
                else:                 
                    return "Not Found", 404
            else:
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

title = "*********************** API Test Server - T. Stewart, 2020 *********************"
print(Style.RESET_ALL + Fore.YELLOW + Style.BRIGHT + title)
print("Supported methods : " + str(methods))
print(Style.RESET_ALL + '', end="")
print("-" * 80)

api = Flask(__name__)
@api.route('/countries', methods=methods)

# all methods
def all_methods():   
    global countries
    if request.method == 'GET':
        return Methods().get(request, countries)
    elif request.method == 'POST':
        return Methods().post(request, countries)
    elif request.method == 'PUT':
        return Methods().put(request, countries)
    elif request.method == 'DELETE':
        return Methods().delete(request, countries)
    elif request.method == 'HEAD':
        return Methods().head(request, countries)
    elif request.method == 'OPTIONS':
        return Methods().options(request)
    elif request.method == 'PATCH':
        return Methods().patch(request, countries)

if __name__ == '__main__':
    api.run()
    #api.run(debug=True)
