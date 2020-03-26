import requests, os, re, sys
from colorama import init, Fore, Back, Style
init()

###############################################################################
# validate request url including endpoint and parameters syntax
def validateRequest(req):
    # try 3 re.search on req for 1) endpt, 2) ? param, 3) & params
    E = re.search(r"http://127\.0\.0\.1:5000/[A-Za-z0-9\_]+", req)
    Q = re.search(r"\?[A-Za-z0-9\_]+=[A-Za-z0-9\_]+", req)
    A = re.search(r"(&[A-Za-z0-9\_]+=[A-Za-z0-9\_]+)+", req)

    # check for basic invalid request syntax
    if E is None or (Q is None and A is not None): 
        result = "Not Found", "404"
    else:
        # too many ? params OR malformed & param
        if (req.count("?") > 1
        or (Q is None and req.find("?") > -1)
        or (A is None and req.find("&") > -1)):
            result = "Not Found", "404"
        else: 
            result = True
    return result

###############################################################################
# display client program header blurb
def printHeader(filename, reqs):
    os.system('cls')
    stars = "*" * 22
    title = stars + " API Test Client - T. Stewart, 2020 " + stars
    print(Style.RESET_ALL + Fore.YELLOW + Style.BRIGHT + title)
    print("Read " + str(len(reqs)) + " requests from file : '" + filename + "'")
    mesg = " *** SERVER LOG DOES NOT SHOW REQUESTS THAT FAILED CLIENT PRE-VALIDATION !!! *** "
    print(Style.RESET_ALL + Fore.RED + Style.BRIGHT + mesg)
    print(Style.RESET_ALL + '', end="")

###############################################################################
# process specified file
def processRequestsFile(filename, reqs):
    printHeader(filename, reqs)
    passed = failed = count = 0
    headers = { "Content-Type": "application/json" }
    for r in reqs:
        response = ""    
        count += 1
        divs = r.split(",")
        validity = validateRequest(divs[1])    

        # the request methods
        if validity == True:
            if divs[0] == "GET":
                response = requests.get(divs[1], headers=headers)
            elif divs[0] == "POST":
                response = requests.post(divs[1], headers=headers)
            elif divs[0] == "PUT":
                response = requests.put(divs[1], headers=headers)
            elif divs[0] == "DELETE":
                response = requests.delete(divs[1], headers=headers)
            elif divs[0] == "PATCH":
                response = requests.patch(divs[1], headers=headers)
            elif divs[0] == "OPTIONS":
                response = requests.options(divs[1], headers=headers)
            elif divs[0] == "HEAD":
                response = requests.head(divs[1], headers=headers)
            else: # mock server response for unavailable request methods
                invalid_request_text = "Bad Request (invalid request method)"
                invalid_request_code = "400"                
        else:
            invalid_request_text = validity[0]
            invalid_request_code = validity[1]

        # get response text and code        
        text = str(response.text) if response != "" else invalid_request_text       
        code = str(response.status_code) if response != "" else invalid_request_code

        # replace longer Not Found blurb
        text = "Not Found (intercepted)" if code == "404" and text != "Not Found" else text 

        # get result and increment passed and failed counters
        result = "PASSED" if divs[2] == code else "FAILED"
        passed += 1 if result == "PASSED" else 0
        failed += 1 if result == "FAILED" else 0

        # print test case result
        if result == "FAILED" or result == "PASSED":
            printTestCaseResult(divs, r, count, text, code, result) 

    # print test results summary
    printTestCasesSummaryResults(count, passed, failed) 

###############################################################################
# print test case result
def printTestCaseResult(divs, r, count, text, code, result):
    print("=" * 80)
    print("TEST #" + str(count) + " : " + r)
    test_result = " : expected status code '" + divs[2] + "', got status code '" + code + "'"
    colour = Fore.RED if result == "FAILED" else Fore.GREEN
    print(Style.RESET_ALL + colour + Style.BRIGHT + result, end="")        
    print(Style.RESET_ALL + test_result)        

    # print line separator if reqd
    if len(text) > 0:
        print("-" * 80)
        print(text)

###############################################################################
# print test results summary
def printTestCasesSummaryResults(count, passed, failed):
    print("=" * 80)
    summary = "FINISHED! - " + str(count) + " tests ran : " + str(passed) + " passed, " + str(failed) + " failed."
    colour = Fore.GREEN if failed == 0 else Fore.RED
    print(Style.RESET_ALL + colour + Style.BRIGHT + summary)
    print(Style.RESET_ALL + '', end="")

###############################################################################
# get command line arguments
def getRequestsFileName(args):
    if len(args) < 2: 
        err = "ERROR : Input file not specified!"
        print(Style.RESET_ALL + Fore.RED + Style.BRIGHT + err)
    else:
        if os.path.exists(args[1]) and os.path.isfile(args[1]):
            reqs = [] # reqs : method,url,expected_status_code
            file_path = args[1]
            with open(file_path,"r") as f:
                reqs = f.read().splitlines()
            processRequestsFile(args[1], reqs)
        else:
            err = "ERROR : Invalid file name specified!"
            print(Style.RESET_ALL + Fore.RED + Style.BRIGHT + err)

###############################################################################
# start
getRequestsFileName(sys.argv)
