from flask import Flask
from flask_restful import Api, Resource, reqparse
import sqlite3

app = Flask(__name__)
api = Api(app)

conn = sqlite3.connect('example.db')
c = conn.cursor()
# Create table
c.execute('''CREATE TABLE IF NOT EXISTS `SpreadSheets` ( `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, `name` VARCHAR UNIQUE NOT NULL , `projectName` VARCHAR NOT NULL )''')
c.execute('''CREATE TABLE IF NOT EXISTS `SpreadSheetsRows` ( `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, `ssId` INTEGER NOT NULL, `boardName` VARCHAR NOT NULL , `width` INTEGER NOT NULL, `height` INTEGER NOT NULL, `boardThickness` REAL NOT NULL, `downCant` REAL NOT NULL, `upCant` REAL NOT NULL, `leftCant` REAL NOT NULL, `rightCant` REAL NOT NULL, `canRotate` BOOLEAN NOT NULL, `boardMaterial` VARCHAR NOT NULL, `holesCount` INTEGER NOT NULL, `holesSide` CHARACTER(20) NOT NULL, UNIQUE(`ssId`, `boardName`) ON CONFLICT ROLLBACK)''')
conn.commit()
conn.close()

spreadsheets = {}
class Spreadsheet(Resource):

    def get(self, spreadSheetName=None, boardName=None):
        if boardName != None:
            for ss in spreadsheets:
                if(boardName == ss["boardName"]):
                    return ss, 200
            return "Board not found", 404
        
        allBoards = []
        for ss in spreadsheets:
            allBoards.append(ss)
        return allBoards, 200           

    def post(self, spreadSheetName, boardName):

        conn = sqlite3.connect('example.db')
        c = conn.cursor()

        c.execute('''INSERT OR IGNORE INTO SpreadSheets(name, projectName) VALUES (?,?)''', (spreadSheetName, ""))
        conn.commit()

        c.execute('''SELECT id FROM SpreadSheets WHERE name=?''', (spreadSheetName,))
        spreadSheetId = c.fetchall()[0][0]
  
        parser = reqparse.RequestParser()
        parser.add_argument("width")
        parser.add_argument("height")
        parser.add_argument("boardThickness")
        parser.add_argument("downCant")
        parser.add_argument("upCant")
        parser.add_argument("leftCant")
        parser.add_argument("rightCant")
        parser.add_argument("canRotate")
        parser.add_argument("boardMaterial")
        parser.add_argument("holesCount")
        parser.add_argument("holesSide")
        args = parser.parse_args()

        ssRec = (spreadSheetId, boardName, args["width"], args["height"], args["boardThickness"], args["downCant"], args["upCant"], args["leftCant"], args["rightCant"], args["canRotate"], args["boardMaterial"], args["holesCount"], args["holesSide"])

        print ssRec

        c.execute('''INSERT OR IGNORE INTO SpreadSheetsRows(ssId,boardName,width,height,boardThickness,downCant,upCant,leftCant,rightCant,canRotate,boardMaterial,holesCount,holesSide) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''', ssRec)        

        conn.commit()
        conn.close()
        return ssRec, 201

#    def put(self, name):
#        parser = reqparse.RequestParser()
#        parser.add_argument("age")
#        parser.add_argument("occupation")
#        args = parser.parse_args()

#        for user in users:
#            if(name == user["name"]):
#                user["age"] = args["age"]
#                user["occupation"] = args["occupation"]
#                return user, 200
        
#        user = {
#            "name": name,
#            "age": args["age"],
#            "occupation": args["occupation"]
#        }
#        users.append(user)
#        return user, 201

#    def delete(self, name):
#        global users
#        users = [user for user in users if user["name"] != name]
#        return "{} is deleted.".format(name), 200

api.add_resource(Spreadsheet, "/ss", "/ss/<string:spreadSheetName>", "/ss/<string:spreadSheetName>/<string:boardName>")

app.run(debug=True)
