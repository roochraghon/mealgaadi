import pyodbc
import json
import os
from flask import Flask
from flask import request
from flask import make_response
from urllib.request import urlopen
app = Flask(__name__)
# connect to database:
def connect(): # function returns cursor
    DRIVER = 'Driver={SQL Server};'
    SERVER = 'Server=ROOCH\\TESTINSTANCE;'
    DATABASE = 'Database=subcat;'
    TRUSTEDCONNECTIONS = 'Trusted_Connection=yes;'
    conn = pyodbc.connect(DRIVER + SERVER + DATABASE + TRUSTEDCONNECTIONS)
    cursor = conn.cursor()
    return cursor

class Menu:
    def __init__(self):
        self.urlMenu = "https://www.mealgaadi.in/Meal_API/products_api.php?query=product_category"
        self.jsonData = json.load(urlopen(self.urlMenu))
    def extractMenu(self):
        menuItems = []
        for menuObject in self.jsonData:
            if menuObject == 'result':
                for block in self.jsonData[menuObject]:
                    for property in block:
                        if property == "name":
                            menuItems.append(block[property])
        return (menuItems)
class Category:
    def extractCatergoryId(self,category):
        query = """select result_category_Id from dbo.mainmenu where result_name = ?"""
        conn = connect()
        conn.execute(query,category)
        for i in conn:
            categoryId = i
        newQuery = """select result_name from dbo.subcategory where result_category_Id=?"""
        conn.execute(newQuery,categoryId)
        ans = []
        for i in conn:
            ans.append(i)
        print(ans)
        return ans



    # def getdata(self):
    #     subCatData = json.load(urlopen(self.urlCategory))
    #     subCatItem = []
    #     for menuObject in subCatData:
    #         if menuObject == 'result':
    #             for block in subCatData[menuObject]:
    #                 for property in block:
    #                     if property == "name":
    #                         subCatItem.append(block[property])
    #     return (subCatItem)


@app.route('/webhook',methods = ['POST'])
def webhook():
    req = request.get_json(silent=True,force=True)
    res = makeWebhookResult(req)
    res = json.dumps(res,indent = 4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeSpeech(result):
    speech = "The details you asked are : \n\n " + ",".join([str(i) for i in list(result)])
    print(speech)
    return {'textToSpeech': speech,'displayText': speech,'fulfillmentText': speech}

def makeWebhookResult(req):
    if req['queryResult']['action'] == 'showMenuAction':
        menu = Menu()
        return makeSpeech( menu.extractMenu())
    elif req['queryResult']['action'] == 'expandMenuAction':
        result = req['queryResult']
        parameters = result.get('parameters')
        category = parameters.get('categoryEntity')
        cat = Category()
        return makeSpeech(cat.extractCatergoryId(category))



if __name__ == "__main__":
    port = int(os.getenv('PORT',80))
    app.run(debug=True,port = port,host = '0.0.0.0')
