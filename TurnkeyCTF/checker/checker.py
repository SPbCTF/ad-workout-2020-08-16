#!/usr/bin/env python3.7
import random
import string
import sys
import requests
import re
import os
import json
import datetime

OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110
SERVICENAME = "TurnkeyCTF"
PORT = "31337"

descr = open("/home/jury/services/turnkeyctf/descr.txt", "r")
descr_text = descr.readlines()
title = open("/home/jury/services/turnkeyctf/title.txt", "r")
title_text = title.readlines()

def close(code, public="", private=""):
    if public:
        print(public)
    if private:
        print(private, file=sys.stderr)
    print('Exit with code {}'.format(code), file=sys.stderr)
    exit(code)


def generate_email():
    return "{}@{}.{}".format(generate_rand(10), generate_rand(5), generate_rand(2))


def generate_rand(N=16):
    return ''.join(random.choice(string.ascii_letters) for i in range(N))

def signin(s,resp, team_addr,username,password):
    match = re.search(r"name=\"csrf_token\".+value=\"([A-z0-9\.-]{80,100})\"", resp.text)

    if match:
        csrf_token = match.group(1)
    else:
        close(CORRUPT, "No csrf token at Sign In page")
    
    resp = s.post("http://{}:{}/signin".format(team_addr, PORT), {
            "username":username,
            "password":password,
            "csrf_token":csrf_token,
            "submit":"Sign In"})

    if not '<title>Task viewer</title>' in resp.text:
        close(CORRUPT, "Sign In failed")
    

def signup(s, team_addr,username,password,email):
    resp = s.get("http://{}:{}/signup".format(team_addr, PORT))
    match = re.search(r"name=\"csrf_token\".+value=\"([A-z0-9\.-]{80,100})\"", resp.text)

    if match:
        csrf_token = match.group(1)
    else:
        close(CORRUPT, "No csrf token at Sign In page")

    resp = s.post("http://{}:{}/signup".format(team_addr, PORT), {
            "firstname":username,
            "lastname":username,
            "username":username,
            "password":password,
            "email": email,
            "csrf_token":csrf_token,
            "submit":"Sign Up"})
    if not 'form-signin' in resp.text:
        close(CORRUPT, "Sign Up failed")

    return resp


def put(*args):
    team_addr, flag_id, flag = args[:3]
    username  = generate_rand()
    password = generate_rand()
    email = generate_email()
    s = requests.Session()

    resp = signup(s,team_addr, username,password,email)
    
    signin(s,resp,team_addr,username,password)  
    
    CTF_templator = s.get("http://{}:{}/CTF_templator".format(team_addr, PORT))
    if not '<title>CTF templator</title>' in CTF_templator.text:
        close(CORRUPT, "Can't open CTF templator")
    now = datetime.datetime.now()
    project = "Project_super_secret_"+str(now.hour) + "_"+str(now.minute)
    params = {"project":project}
    resp = s.get("http://{}:{}/project_selection".format(team_addr, PORT), params=params)
    if not 'New project created' in resp.text:
        close(CORRUPT, "Can't create project")    

    matches = re.findall(r"class=\"list-group-item\" id=\"([a-z0-9]{24})", CTF_templator.text, re.MULTILINE)
    task_id = matches[random.randint(0,len(matches)-1)]
    params = {"id": task_id}
    resp = s.get("http://{}:{}/get_info".format(team_addr, PORT), params=params)
    if not all(x in resp.text for x in ['Category', 'Description', 'Flag', 'Name']):
        close(MUMBLE, "Can't get one of the tasks")  
    y = json.loads(resp.text)["result"]
    resp = s.post("http://{}:{}/save_task".format(team_addr, PORT), {
        "id":task_id,
        "Name":y["Name"],
        "Description":y["Description"],
        "Flag":flag,
        "Category": y["Category"],
        "Category_full":y["Category_full"],
        "Project":project})
    
    if not "success" in resp.text:
        close(MUMBLE, "Can't save task in project")  

    close(OK, "{}:{}:{}".format(username, password, project))


def get(*args):
    team_addr, lpb, flag = args[:3]
    s = requests.Session()    
    username, password, project = lpb.split(":")


    resp = s.get("http://{}:{}/signin".format(team_addr, PORT))
    signin(s,resp,team_addr,username,password)  
    
    params = {"project":project}
    resp = s.get("http://{}:{}/project_selection".format(team_addr, PORT), params=params)
    if not 'result' in resp.text:
        close(CORRUPT, "Cant create project")    

    tasks = json.loads(resp.text)["result"]
    tasks = map(lambda d: d['_id'], tasks)
    for task_id in tasks:
        params = {"id": task_id}
        resp = s.get("http://{}:{}/get_info".format(team_addr, PORT), params=params)
        if not all(x in resp.text for x in ['Category', 'Description', 'Flag', 'Name']):
            close(MUMBLE, "Cant get one of the tasks")  
        y = json.loads(resp.text)["result"]
        if y['Flag']==flag:
            close(OK)
    close(CORRUPT, "No flag in the project found")


def error_arg(*args):
    close(CHECKER_ERROR, private="Wrong command {}".format(sys.argv[1]))


def info(*args):
    close(OK, "vulns: 1")


def check(*args):
    username  = generate_rand()
    password = generate_rand()
    email = generate_email()
    team_addr = args[:1][0]
    s = requests.Session()  
    resp = s.get("http://{}:{}/".format(team_addr, PORT))
    if not resp.status_code == 200:
        close(CORRUPT, "Cant load index, lol")
    resp = signup(s,team_addr, username,password,email)
    
    signin(s,resp,team_addr,username,password)  

        
    resp = s.get("http://{}:{}/add_task".format(team_addr, PORT))
    if not resp.status_code == 200:
        close(CORRUPT, "Cant load add task page")
    category = random.choice(list(categories.items()))
    resp = s.post("http://{}:{}/add_task_handler".format(team_addr, PORT), {
            "Name":random.choice(title_text),
            "Description":random.choice(descr_text),
            "Flag":"totally_not_a_flag_"+str(generate_rand()),
            "Category":category[0],
            "Category_full": category[1]})

    if not "success" in resp.text:
        close(MUMBLE, "Can't add task")  
    
    resp = s.get("http://{}:{}/edit_task".format(team_addr, PORT))
    if not resp.status_code == 200:
        close(CORRUPT, "Cant load add task page")

    close(OK, "ok")

def init(*args):
    close(OK)

categories = {"Web":"Web", "Rev":"Reverse", "HTB":"HTB", "Steg":"Steganography", "Cryp":"Cryptography", "Misc":"Misc" , "Joy":"Joy", "PWN":"PWN"}
            

COMMANDS = {
    'put': put,
    'check': check,
    'get': get,
    'info': info,
    'init': init
}


if __name__ == '__main__':
    try:
        COMMANDS.get(sys.argv[1], error_arg)(*sys.argv[2:])
    except Exception as ex:
        close(CHECKER_ERROR, private="INTERNAL ERROR: {}".format(ex))
