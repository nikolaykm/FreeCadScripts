def writeRecordInSpreadsheet(spreadsheetName, recArr):
    #find next empty row
    row = 1
    while(True):
        try:
            if getattr(App.activeDocument(), spreadsheetName).get('A' + str(row)) == '':
                break; 
            row = row + 1
        except ValueError:
            break

    column = ord('A')
    for item in recArr:
        getattr(App.activeDocument(), spreadsheetName).set(chr(column) + str(row), str(item))
        column = column + 1

    App.ActiveDocument.recompute()

    return row

def getRowFromSpreadsheet(spreadsheetName, row):
    resultDict = dict()
    column = ord('A')
    while(True):
        try:
            key = getattr(App.activeDocument(), spreadsheetName).get(chr(column) + str(1))
        except ValueError:
            break

        try:
            value = getattr(App.activeDocument(), spreadsheetName).get(chr(column) + str(row))
        except ValueError:
            value = ""

        resultDict[key] = value
        column = column + 1

    return resultDict

def createBody(bodyName):
    App.activeDocument().addObject('PartDesign::Body', bodyName)
    App.ActiveDocument.recompute()

def createSketch(sketchName, bodyName, supportName, supportFace):
    getattr(App.activeDocument(), bodyName).newObject('Sketcher::SketchObject', sketchName)
    getattr(App.activeDocument(), sketchName).Support = (getattr(App.activeDocument(), supportName), [str(supportFace)])
    getattr(App.activeDocument(), sketchName).MapMode = 'FlatFace'
    App.ActiveDocument.recompute()

def createRectInSketch(sketchName, xL, yL, extraConList):
    geoList = []
    geoList.append(Part.LineSegment(App.Vector(-1,1,0),App.Vector(1,1,0)))
    geoList.append(Part.LineSegment(App.Vector(1,1,0),App.Vector(1,-1,0)))
    geoList.append(Part.LineSegment(App.Vector(1,-1,0),App.Vector(-1,-1,0)))
    geoList.append(Part.LineSegment(App.Vector(-1,-1,0),App.Vector(-1,1,0)))
    getattr(App.activeDocument(), sketchName).addGeometry(geoList,False)
    conList = []
    conList.append(Sketcher.Constraint('Coincident',0,2,1,1))
    conList.append(Sketcher.Constraint('Coincident',1,2,2,1))
    conList.append(Sketcher.Constraint('Coincident',2,2,3,1))
    conList.append(Sketcher.Constraint('Coincident',3,2,0,1))
    conList.append(Sketcher.Constraint('Horizontal',0))
    conList.append(Sketcher.Constraint('Horizontal',2))
    conList.append(Sketcher.Constraint('Vertical',1))
    conList.append(Sketcher.Constraint('Vertical',3))
    conList.append(Sketcher.Constraint('DistanceX',0,1,0,2,xL))
    conList.append(Sketcher.Constraint('DistanceY',1,2,1,1,yL))
    conList.extend(extraConList)
    getattr(App.activeDocument(), sketchName).addConstraint(conList)
    App.ActiveDocument.recompute()

def createPadFromSketch(bodyName, sketchName, zL):
    padName = sketchName + "_Pad"
    getattr(App.activeDocument(), bodyName).newObject("PartDesign::Pad", padName)
    getattr(App.activeDocument(), padName).Profile = getattr(App.activeDocument(), sketchName)
    getattr(App.activeDocument(), padName).Length = zL
    getattr(App.activeDocument(), padName).Length2 = 100.000000
    getattr(App.activeDocument(), padName).Type = 0
    getattr(App.activeDocument(), padName).UpToFace = None
    getattr(App.activeDocument(), padName).Reversed = 0
    getattr(App.activeDocument(), padName).Midplane = 0
    getattr(App.activeDocument(), padName).Offset = 0.000000

    App.ActiveDocument.recompute()


def createBoard(cabinetName, bodyName, row):

    rowDict = getRowFromSpreadsheet(cabinetName + "_Spreadsheet", row)
    sketchName = rowDict['Name']
    xL = rowDict['Width']
    yL = rowDict['Height']
    zL = rowDict['BoardThickness']

    #create the board
    createSketch(sketchName, bodyName, 'XY_Plane', '')
    conList = []
    conList.append(Sketcher.Constraint('Symmetric',0,1,1,2,-1,1))
    createRectInSketch(sketchName, xL, yL, conList)
    createPadFromSketch(bodyName, sketchName, zL)

    #cant the board
    cantToFaceDict = {'WCantFront' : 'Face3', 'WCantBack' : 'Face1', 'HCantLeft' : 'Face4', 'HCantRight' : 'Face2'}
    for cant,face in cantToFaceDict.items():
        if rowDict[cant] != "" and rowDict[cant] != "0" and rowDict[cant] != 0:
            cantSketchName = sketchName + "_" + cant
            createSketch(cantSketchName, bodyName, sketchName + "_Pad", face)
            width = rowDict['Width'] if (cant == 'WCantFront' or cant == 'WCantBack') else rowDict['Height']
            conList = []
            conList.append(Sketcher.Constraint('DistanceY',-1,1,0,1,rowDict['BoardThickness']));
            conList.append(Sketcher.Constraint('DistanceX',0,1,-1,1,width/2))
            createRectInSketch(cantSketchName, width, rowDict['BoardThickness'], conList)
            createPadFromSketch(bodyName, cantSketchName, rowDict[cant])
            

def createBaseCabinet(name, width, height, depth, boardThickness, sCantT, lCantT, legHeight):

    #create spreadsheet column names
    App.activeDocument().addObject('Spreadsheet::Sheet', name + "_Spreadsheet")
    spreadSheetHeaders = ['Name', 'Width', 'Height', 'BoardThickness', 'WCantFront', 'WCantBack', 'HCantLeft', 'HCantRight', 'ByFlader']
    writeRecordInSpreadsheet(name + "_Spreadsheet", spreadSheetHeaders)
    
    #create base
    bodyName = name + "_Base";
    createBody(bodyName)
    cants = [sCantT, sCantT, sCantT, sCantT]
    cantToFaceDict = {'WCantFront' : 'Face3', 'WCantBack' : 'Face1', 'HCantLeft' : 'Face4', 'HCantRight' : 'Face2'}
    calcWidth = width-cants[2]-cants[3];
    calcHeight = depth-cants[0]-cants[1]
    sprRec = [bodyName + '_SketchBase', calcWidth, calcHeight, boardThickness, cants[0], cants[1], cants[2], cants[3], 0]
    row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
    createBoard(name, bodyName, row)

    #TODO: cant the upper side
    #create left side
    bodyName = name + "_LeftSide"
    createBody(bodyName)
    cants = [0, 0, sCantT, sCantT]
    calcWidth = depth-cants[2]-cants[3]
    calcHeight = height-cants[0]-cants[1]-boardThickness-legHeight
    sprRec = [bodyName + '_SketchLeftSide', calcWidth, calcHeight, boardThickness, cants[0], cants[1], cants[2], cants[3], 1]
    row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
    createBoard(name, bodyName, row)
    getattr(App.activeDocument(), bodyName).Placement=App.Placement(App.Vector(-width/2,0,calcHeight/2+boardThickness), App.Rotation(90,0,90), App.Vector(0,0,0))
    App.ActiveDocument.recompute()

    #TODO: cant the upper side
    #create right side
    bodyName = name + "_RightSide"
    createBody(bodyName)
    cants = [0, 0, sCantT, sCantT]
    calcWidth = depth-cants[2]-cants[3]
    calcHeight = height-cants[0]-cants[1]-boardThickness-legHeight
    sprRec = [bodyName + '_SketchRightSide', calcWidth, calcHeight, boardThickness, cants[0], cants[1], cants[2], cants[3], 1]
    row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
    createBoard(name, bodyName, row)
    getattr(App.activeDocument(), bodyName).Placement=App.Placement(App.Vector(width/2,0,calcHeight/2+boardThickness), App.Rotation(90,0,-90), App.Vector(0,0,0))
    App.ActiveDocument.recompute()

    #create front up
#    createSketch(name + '_SketchFrontUp', name, name + '_SketchLeftSide_Pad', 'Face9')
#    conList = []
#    conList.append(Sketcher.Constraint('Distance',-1,1,3,depth/2))
#    conList.append(Sketcher.Constraint('DistanceY',-1,1,0,1,height + boardThickness))
#    cantsList = [sCantT, sCantT, sCantT, sCantT]
#    createBoard(100, boardThickness, width-2*boardThickness, cantsList, name, name + '_SketchFrontUp', name + '_SketchFrontUp_Pad', conList)

    #create back up
#    createSketch(name + '_SketchBackUp', name, name + '_SketchLeftSide_Pad', 'Face9')
#    conList = []
#    conList.append(Sketcher.Constraint('Distance',-1,1,1,depth/2))
#    conList.append(Sketcher.Constraint('DistanceY',-1,1,0,1,height + boardThickness))
#    cantsList = [sCantT, sCantT, sCantT, sCantT]
#    createBoard(100, boardThickness, width-2*boardThickness, cantsList, name, name + '_SketchBackUp', name + '_SketchBackUp_Pad', conList)

    #create back
#    createSketch(name + '_SketchBack', name, name + '_SketchBase_Pad', 'Face1')
#    conList = []
#    conList.append(Sketcher.Constraint('Distance',-1,1,1,width/2))
#    conList.append(Sketcher.Constraint('DistanceY',-1,1,0,1,height + boardThickness))
#    cantsList = [sCantT, sCantT, sCantT, sCantT]
#    createBoard(width, height, 3, cantsList, name, name + '_SketchBack', name + '_SketchBack_Pad', conList)

createBaseCabinet("BottlesLeft", 600, 750, 520, 18, 0.8, 2, 100)
