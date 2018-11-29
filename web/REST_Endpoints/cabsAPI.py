from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS
import sqlite3


app = Flask(__name__)
CORS(app)
api = Api(app)

conn = sqlite3.connect('example.db')
c = conn.cursor()
# Create table
c.execute('''CREATE TABLE IF NOT EXISTS `SpreadSheets` ( `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, `name` VARCHAR UNIQUE NOT NULL , `projectName` VARCHAR NOT NULL )''')
c.execute('''CREATE TABLE IF NOT EXISTS `SpreadSheetsRows` ( `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, `ssId` INTEGER NOT NULL, `boardName` VARCHAR NOT NULL , `width` INTEGER NOT NULL, `height` INTEGER NOT NULL, `boardThickness` REAL NOT NULL, `downCant` REAL NOT NULL, `upCant` REAL NOT NULL, `leftCant` REAL NOT NULL, `rightCant` REAL NOT NULL, `byFlader` BOOLEAN NOT NULL, `boardMaterial` VARCHAR NOT NULL, `holesCount` INTEGER NOT NULL, `holesSide` CHARACTER(20) NOT NULL, UNIQUE(`ssId`, `boardName`) ON CONFLICT ROLLBACK)''')
conn.commit()
conn.close()

spaceBetweenDoors = 3.0

class Spreadsheet(Resource):

    def get(self, spreadSheetName=None, boardName=None):

        if spreadSheetName == None:
            conn = sqlite3.connect('example.db')
            c = conn.cursor()

            c.execute('''SELECT name FROM SpreadSheets''')
            conn.commit()

            result = c.fetchall()

            conn.close()

            return result, 200

        conn = sqlite3.connect('example.db')
        c = conn.cursor()

        c.execute('''SELECT id FROM SpreadSheets WHERE name=?''', (spreadSheetName, ))
        conn.commit()
        ssId = c.fetchall()[0][0]

        selectRowsParams = [ssId] if boardName != None else [ssId,]
        selectRowsString = ''' SELECT * FROM SpreadSheetsRows WHERE ssId=?  '''

        if boardName != None:
            selectRowsParams.append(boardName)
            selectRowsString = selectRowsString + " AND boardName=? "

        c.execute(selectRowsString, tuple(selectRowsParams))
        allBoards = c.fetchall()

        c.execute("PRAGMA table_info(SpreadSheetsRows)")
        columnNames = c.fetchall();

        resultList = []
        for board in allBoards:
            boardDict = dict()
            for column in columnNames:
                boardDict[column[1]] = board[column[0]]
            resultList.append(boardDict)

        conn.close()
        return resultList, 200

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
        parser.add_argument("byFlader")
        parser.add_argument("boardMaterial")
        parser.add_argument("holesCount")
        parser.add_argument("holesSide")
        args = parser.parse_args()

        ssRec = (spreadSheetId, boardName, args["width"], args["height"], args["boardThickness"], args["downCant"], args["upCant"], args["leftCant"], args["rightCant"], args["byFlader"], args["boardMaterial"], args["holesCount"], args["holesSide"])

        print ssRec

        c.execute('''INSERT OR IGNORE INTO SpreadSheetsRows(ssId,boardName,width,height,boardThickness,downCant,upCant,leftCant,rightCant,byFlader,boardMaterial,holesCount,holesSide) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''', ssRec)        

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


class Board(Resource):

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("width")
        parser.add_argument("height")
        parser.add_argument("boardThickness")
        parser.add_argument("downCant")
        parser.add_argument("upCant")
        parser.add_argument("leftCant")
        parser.add_argument("rightCant")
        parser.add_argument("cantsSubstracted")
        args = parser.parse_args()

        widthWithoutCants = round(float(args["width"]) - ((float(args["leftCant"]) + float(args["rightCant"])) if args["cantsSubstracted"] != "1" else 0))
        heightWithoutCants = round(float(args["height"]) - ((float(args["downCant"]) + float(args["upCant"])) if args["cantsSubstracted"] != "1" else 0))

        resultDict = {}

        resultDict['board'] = { 'width' : float(widthWithoutCants), 
                                'height' : float(heightWithoutCants), 
                                'depth': float(args["boardThickness"]), 
                                'pos': (0, 0, 0), 
                                'rot' : (0, 0, 0)}

        leftCant = { 'width' : float(heightWithoutCants), 
                     'height' : float(args["boardThickness"]), 
                     'depth': float(args["leftCant"]),
                     'pos': (-widthWithoutCants/2.0, 0, float(args["boardThickness"])/2),
                     'rot' : (90, 0, -90)}

        rightCant = { 'width' : float(heightWithoutCants),
                      'height' : float(args["boardThickness"]),
                      'depth': float(args["rightCant"]),
                      'pos': (widthWithoutCants/2.0, 0, float(args["boardThickness"])/2), 
                      'rot' : (90, 0, 90)}

        downCant =  { 'width' : float(widthWithoutCants),
                      'height' : float(args["boardThickness"]),
                      'depth': float(args["downCant"]),
                      'pos': (0, -heightWithoutCants/2.0, float(args["boardThickness"])/2),
                      'rot' : (0, 0, 90)}

        upCant =    { 'width' : float(widthWithoutCants),
                      'height' : float(args["boardThickness"]),
                      'depth': float(args["upCant"]),
                      'pos': (0, heightWithoutCants/2.0, float(args["boardThickness"])/2),
                      'rot' : (0, 0, -90)}

        resultDict['cants'] = { 'leftCant' : leftCant, 'rightCant' : rightCant, 'downCant' : downCant, 'upCant' : upCant }

        return resultDict


class Cab(Resource):

    def get(self):
        addOns = dict()

        parser = reqparse.RequestParser()
        parser.add_argument("width", required=True, help="Width cannot be blank!")
        parser.add_argument("height", required=True, help="Height cannot be blank!")
        parser.add_argument("depth", required=True, help="Depth cannot be blank!")
        parser.add_argument("visibleBack")
        parser.add_argument("isBase")
        parser.add_argument("isHavingBack")
        parser.add_argument("shiftBlend")
        parser.add_argument("haveWholeBlend")
        parser.add_argument("legHeight")
        parser.add_argument("sCantT")
        parser.add_argument("lCantT")
        parser.add_argument("boardThickness")
        parser.add_argument("cardboardThickness")
        parser.add_argument("material")
        parser.add_argument("cardboardMaterial")
        parser.add_argument("doorsMaterial")
        parser.add_argument("doors")
        parser.add_argument("shelves")
        args = parser.parse_args()

        width = float(args['width'])
        height = float(args['height'])
        depth = float(args['depth'])
        visibleBack = bool(args['visibleBack']) if args['visibleBack'] != None else False
        isBase = bool(args['isBase']) if args['isBase'] != None else True
        isHavingBack = bool(args['isHavingBack']) if args['isHavingBack'] != None else True
        shiftBlend = float(args['shiftBlend']) if args['shiftBlend'] != None else 0.0
        haveWholeBlend = bool(args['haveWholeBlend']) if args['haveWholeBlend'] != None else False
        legHeight = float(args['legHeight']) if args['legHeight'] != None else 100.0
        sCantT = float(args['sCantT']) if args['sCantT'] != None else 0.8
        lCantT = float(args['lCantT']) if args['lCantT'] != None else 2.0
        boardThickness = float(args['boardThickness']) if args['boardThickness'] != None else 18.0
        cardboardThickness = float(args['cardboardThickness']) if args['cardboardThickness'] != None else 3.0
        material = args['material'] if args['material'] != None else ""
        cardboardMaterial = args['cardboardMaterial'] if args['cardboardMaterial'] != None else "_cardboard"
        doorsMaterial = args['doorsMaterial'] if args['doorsMaterial'] != None else ""
        doors = int(args['doors']) if args['doors'] != None else 0
        shelves = int(args['shelves']) if args['shelves'] != None else 0


        resultDict = {}

        resultDict['boards'] = [] 

        #create base
        cants = { 'downCant' : sCantT, 'upCant' : sCantT if visibleBack else 0, 'leftCant' : sCantT, 'rightCant' : sCantT }
        baseCants = cants
        baseWidth = calcWidth = width;
        baseHeight = calcHeight = depth-(0 if visibleBack else cardboardThickness)
        resultDict['boards'].append({ 'name' : '_Base', 
                                      'width' : calcWidth, 
                                      'height' : calcHeight, 
                                      'cants' : cants, 
                                      'material' : material, 
                                      'fladderSide' : "W", 
                                      'thickness' : boardThickness,
                                      'pos' : (0, 0, 0), 
                                      'rot' : (0, 0, 0)})

        #create left side
        cants = { 'downCant' : 0, 'upCant' : 0 if isBase else sCantT, 'leftCant' : sCantT, 'rightCant' : sCantT if visibleBack else 0 }
        calcWidth = depth-(0 if visibleBack else cardboardThickness)
        calcHeight = height-boardThickness-(legHeight if isBase else 0)
        resultDict['boards'].append({ 'name' : '_LeftSide', 
                                      'width' : calcWidth, 
                                      'height' : calcHeight, 
                                      'cants' : cants, 
                                      'material' : material, 
                                      'fladderSide' : "H",
                                      'thickness' : boardThickness,
                                      'pos' : (-width/2, 0, calcHeight/2+boardThickness),
                                      'rot' : (90, 0, 90)})

        #create right side
        cants = { 'downCant' : 0 if isBase else sCantT, 'upCant' : 0, 'leftCant' : sCantT, 'rightCant' : sCantT if visibleBack else 0 }
        calcWidth = depth-(0 if visibleBack else cardboardThickness)
        calcHeight = height-boardThickness-(legHeight if isBase else 0)
        resultDict['boards'].append({ 'name' : '_RightSide',
                                      'width' : calcWidth, 
                                      'height' : calcHeight, 
                                      'cants' : cants, 
                                      'material' : material, 
                                      'fladderSide' : "H",
                                      'thickness' : boardThickness,
                                      'pos' : (width/2, 0, calcHeight/2+boardThickness),
                                      'rot' : (90, 0, -90)})

        if isBase and not haveWholeBlend:
            #create front blend
            cants = { 'downCant' : sCantT, 'upCant' : 0, 'leftCant' : 0, 'rightCant' : 0 }
            calcWidth = width-2*boardThickness;
            calcHeight = 100
            resultDict['boards'].append({'name' : "_FrontBlend", 
                                         'width' : calcWidth, 
                                         'height' : calcHeight, 
                                         'cants' : cants, 
                                         'material' : material, 
                                         'fladderSide' : "-",
                                         'thickness' : boardThickness,
                                         'pos' : (0, -baseHeight/2+calcHeight/2, height-legHeight-boardThickness), 
                                         'rot' : (0, 0, 0)})

            #create back blend
            cants = { 'downCant' : 0, 'upCant' : sCantT if visibleBack else 0, 'leftCant' : 0, 'rightCant' : 0 }
            calcWidth = width-2*boardThickness;
            calcHeight = 100
            resultDict['boards'].append({'name' : "_BackBlend", 
                                         'width' : calcWidth, 
                                         'height' : calcHeight, 
                                         'cants' : cants, 
                                         'material' : material, 
                                         'fladderSide' : "-",
                                         'thickness' : boardThickness,
                                         'pos' : (0, baseHeight/2-calcHeight/2, height-legHeight-boardThickness),
                                         'rot' : (0, 0, 0)})
        else:
            #create whole blend
            cants = { 'downCant' : sCantT, 'upCant' : sCantT if visibleBack else 0, 'leftCant' : 0, 'rightCant' : 0 }
            calcWidth = width-2*boardThickness;
            calcHeight = baseHeight
            resultDict['boards'].append({'name' : "_WholeBlend", 
                                         'width' : calcWidth, 
                                         'height' : calcHeight, 
                                         'cants' : cants, 
                                         'material' : material, 
                                         'fladderSide' : "W",
                                         'thickness' : boardThickness,
                                         'pos' : (0, 0, height-boardThickness-shiftBlend-(legHeight if isBase else 0)),
                                         'rot' : (0, 0, 0)})


        if isHavingBack:
            cants = { 'downCant' : 0, 'upCant' : 0, 'leftCant' : 0, 'rightCant' : 0 }

            if not visibleBack:
                #create back from cardboard
                calcWidth = width - 3;
                calcHeight = height-(legHeight if isBase else 0)-3
                resultDict['boards'].append({'name' : '_Back',  
                                             'width' : calcWidth, 
                                             'height' : calcHeight, 
                                             'cants' : cants, 
                                             'material' : material+"_card", 
                                             'fladderSide' : "H", 
                                             'thickness' : cardboardThickness,
                                             'pos' : (0, baseHeight/2+cardboardThickness, height/2-(legHeight if isBase else 0)/2),
                                             'rot' : (0, 90, 0) })
            else:
                #create back from normal board
                calcWidth = width-2*boardThickness;
                calcHeight = height-(legHeight if isBase else 0)-2*boardThickness
                resultDict['boards'].append({'name' : '_Back',
                                             'width' : calcWidth,
                                             'height' : calcHeight,
                                             'cants' : cants,
                                             'material' : material+"_card",
                                             'fladderSide' : "H",
                                             'thickness' : boardThickness,
                                             'pos' : (0, baseHeight/2+baseCants['upCant'], height/2-(legHeight if isBase else 0)/2), 
                                             'rot' : (0, 90, 0) })


        if 'list' not in addOns:
            addOns['list'] = []

        if doors > 0:
            calcWidth = width/doors - spaceBetweenDoors - (spaceBetweenDoors/(2*doors) if 'doorsWallRight' in addOns else 0) - (spaceBetweenDoors/(2*doors) if 'doorsWallLeft' in addOns else 0)
            calcHeight = height-((legHeight+2) if isBase else 0)-spaceBetweenDoors
            for curDoor in range(0, doors):
                xPos = calcWidth*curDoor + calcWidth/2 - width/2 + spaceBetweenDoors/2
                if curDoor == 0 and 'doorsWallLeft' in addOns: xPos = xPos + spaceBetweenDoors/2
                if curDoor != 0: xPos = xPos + spaceBetweenDoors
                doorsHoles = addOns['doorsHoles'] if 'doorsHoles' in addOns else 0
                doorsHolesSide = addOns['doorsHolesSide'] if 'doorsHolesSide' in addOns else '-'
                addOns['list'].append(["_Door" + str(curDoor+1), calcWidth, calcHeight, {'downCant' : lCantT, 'upCant' : lCantT, 'leftCant' : lCantT, 'rightCant' : lCantT}, xPos, 0, 0, True, doorsHoles, doorsHolesSide])

        if shelves > 0:
            calcWidth = width - 2*boardThickness
            calcHeight = depth - (boardThickness if visibleBack else cardboardThickness) - sCantT
            for curShelf in range(1, shelves+1):
                yPos = (sCantT - boardThickness/2) if visibleBack else sCantT/2
                zPos = ((height-(legHeight if isBase else 0))/(shelves+1))*curShelf
                addOns['list'].append(["_Shelf" + str(curShelf), calcWidth, calcHeight, {'downCant' : sCantT, 'upCant' : 0, 'leftCant' : 0, 'rightCant' : 0}, 0, yPos, zPos, False])

        #create addOns
        for addOn in addOns['list']:
            doorsHoles = addOn[8] if len(addOn) >= 9 else 0
            doorsHolesSide = addOn[9] if len(addOn) >= 10 else '-'
            xPos = addOn[4]
            yPos = ((-baseHeight/2-baseCants['downCant']-2) if addOn[7] else 0) + addOn[5]
            zPos = ((height/2 - ((legHeight+2) if isBase else 0)/2) if addOn[7] else 0) + addOn[6]
            resultDict['boards'].append({'name' : addOn[0], 
                                         'width' : addOn[1], 
                                         'height' : addOn[2], 
                                         'cants' : addOn[3], 
                                         'material' : doorsMaterial if addOn[7] else material, 
                                         'fladderSide' : 'H' if addOn[7] else 'W', 
                                         'thickness' : boardThickness, 
                                         'doorHoles' : doorsHoles, 
                                         'doorHolesSide' : doorsHolesSide,
                                         'pos' : (xPos, yPos, zPos),
                                         'rot' : (0, (90 if addOn[7] else 0), 0)})

        return resultDict


api.add_resource(Spreadsheet, "/ss", "/ss/<string:spreadSheetName>", "/ss/<string:spreadSheetName>/<string:boardName>")
api.add_resource(Board, "/board")
api.add_resource(Cab, "/cab")

app.run(debug=True)
