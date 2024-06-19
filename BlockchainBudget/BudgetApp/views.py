from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from datetime import date
import os
import json
from web3 import Web3, HTTPProvider

global details, username, limit
details=''
global contract

def readDetails(contract_type):
    global details
    details = ""
    print(contract_type+"======================")
    blockchain_address = 'http://127.0.0.1:9545' #Blokchain connection IP
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'BudgetContract.json' #BudgetContract contract code
    deployed_contract_address = '0x01Af530f2EA7a4153D9592d96A1451D6A773Ca3a' #hash address to access Budget contract
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi) #now calling contract to access data
    if contract_type == 'users':
        details = contract.functions.getUsers().call()
    if contract_type == 'budget':
        details = contract.functions.getBudgetDetails().call()
    print(details)    

def saveDataBlockChain(currentData, contract_type):
    global details
    global contract
    details = ""
    blockchain_address = 'http://127.0.0.1:9545'
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'BudgetContract.json' #BudgetContract contract file
    deployed_contract_address = '0x01Af530f2EA7a4153D9592d96A1451D6A773Ca3a' #contract address
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
    readDetails(contract_type)
    if contract_type == 'users':
        details+=currentData
        msg = contract.functions.addUsers(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    if contract_type == 'budget':
        details+=currentData
        msg = contract.functions.addBudgetDetails(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)        

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})    

def Login(request):
    if request.method == 'GET':
        return render(request, 'Login.html', {})
    
def Register(request):
    if request.method == 'GET':
        return render(request, 'Register.html', {})

def AddBudget(request):
    if request.method == 'GET':
       return render(request, 'AddBudget.html', {})

def AddBudgetAction(request):
    if request.method == 'POST':
        global username
        name = request.POST.get('t1', False)
        amount = request.POST.get('t2', False)
        desc = request.POST.get('t3', False)
        today = date.today()
        data = username+"#"+name+"#"+amount+"#"+desc+"#"+str(today)+"\n"
        saveDataBlockChain(data,"budget")
        context= {'data': 'Budget details saved in Blockchain'}
        return render(request, 'AddBudget.html', context)
        
def Signup(request):
    if request.method == 'POST':
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        contact = request.POST.get('contact', False)
        email = request.POST.get('email', False)
        address = request.POST.get('address', False)
        limit = request.POST.get('limit', False)
        record = 'none'
        readDetails("users")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[1] == username:
                record = "exists"
                break
        if record == 'none':
            data = username+"#"+password+"#"+contact+"#"+email+"#"+address+"#"+limit+"\n"
            saveDataBlockChain(data,"users")
            context= {'data':'Signup process completed and record saved in Blockchain'}
            return render(request, 'Register.html', context)
        else:
            context= {'data':username+'Username already exists'}
            return render(request, 'Register.html', context)
        
def UserLogin(request):
    if request.method == 'POST':
        global username, limit
        limit = 0
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        status = 'none'
        readDetails("users")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == username and arr[1] == password:
                status = 'success'
                limit = arr[5]
                break
        if status == 'success':
            context= {'data':"Welcome "+username}
            return render(request, 'UserScreen.html', context)
        else:
            context= {'data':"Invalid Login"}
            return render(request, 'Login.html', context)                
            
        
def getExpenditure(exp, dd):
    amount = 0
    for i in range(len(exp)):
        amt = exp[i]
        value = amt[0]
        if value == dd:
            amount = str(amt[1])
            break
    return amount        

def TrackBudget(request):
    if request.method == 'GET':
        global username, limit
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Username</font></th>'
        output+='<th><font size=3 color=black>Budget Name</font></th>'
        output+='<th><font size=3 color=black>Amount</font></th>'
        output+='<th><font size=3 color=black>Description</font></th>'
        output+='<th><font size=3 color=black>Budget Feed Date</font></th></tr>'
        readDetails("budget")
        rows = details.split("\n")
        dates = []
        expenditure = []
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == username:
                dd = arr[4].split("-")
                temp = dd[0]+"-"+dd[1]
                if temp not in dates:
                    dates.append(temp)
        for i in range(len(dates)):
            amount = 0
            for j in range(len(rows)-1):
                arr = rows[j].split("#")
                if arr[0] == username:
                    dd = arr[4].split("-")
                    temp = dd[0]+"-"+dd[1]
                    if dates[i] == temp:
                        amount = amount + float(arr[2])
            expenditure.append([dates[i], amount])
        dup = []
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == username:
                dd = arr[4].split("-")
                temp = dd[0]+"-"+dd[1]
                if temp not in dup:
                    exp_value = getExpenditure(expenditure, temp)
                    output+='<tr><td><font size=3 color=red>Max Limit = '+str(limit)+'</font></td>'
                    output+='<td><font size=3 color=red>Expenditure for '+temp+' = '+str(exp_value)+'</font></td></tr>' 
                    dup.append(temp)
                output+='<tr><td><font size=3 color=black>'+arr[0]+'</font></td>'
                output+='<td><font size=3 color=black>'+arr[1]+'</font></td>'
                output+='<td><font size=3 color=black>'+arr[2]+'</font></td>'
                output+='<td><font size=3 color=black>'+arr[3]+'</font></td>'
                output+='<td><font size=3 color=black>'+arr[4]+'</font></td></tr>'
        context= {'data': output}        
        return render(request, 'UserScreen.html', context)


        
            
