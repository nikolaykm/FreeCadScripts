from flask import Flask
from flask_restful import Api, Resource, reqparse
import sqlite3

app = Flask(__name__)
api = Api(app)

spreadsheets = {}
class Spreadsheet(Resource):

    def get(self, boardName=None):
        if boardName != None:
            for ss in spreadsheets:
                if(boardName == ss["boardName"]):
                    return ss, 200
            return "Board not found", 404
        
        allBoards = []
        for ss in spreadsheets:
            allBoards.append(ss)
        return allBoards, 200           

    def post(self, boardName):
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

        for ss in spreadsheets:
            if(boardName == ss["boardName"]):
                return "Board with name {} already exists".format(boardName), 400

        ssRec = {
            "boardName": boardName,
            "width": args["width"],
            "height": args["height"],
            "boardThickness": args["boardThickness"],
            "downCant": args["downCant"],
            "upCant": args["upCant"],
            "leftCant": args["leftCant"],
            "rightCant": args["rightCant"],
            "canRotate": args["canRotate"],
            "boardMaterial": args["boardMaterial"],
            "holesCount": args["holesCount"],
            "holesSide": args["holesSide"]
        }
        spreadsheets.append(ssRec)
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

conn = sqlite3.connect('example.db')
c = conn.cursor()
# Create table
c.execute('''CREATE TABLE IF NOT EXISTS Spreadsheets
             (idx int, name text)''')

api.add_resource(Spreadsheet, "/ss", "/ss/<string:spreadSheetName>", "/ss/<string:spreadSheetName>/<string:boardName>")

app.run(debug=True)
