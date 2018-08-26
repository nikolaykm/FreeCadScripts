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

def createCircleInSketch(sketchName, radius):
    getattr(App.activeDocument(), sketchName).addGeometry(Part.Circle(App.Vector(0,0,0),App.Vector(0,0,1),radius),False)
    getattr(App.activeDocument(), sketchName).addConstraint(Sketcher.Constraint('Coincident',0,3,-1,1))

def createLeg(cabinetName, bodyName, radius, legHeight):
    createBody(bodyName)
    sketchName = bodyName+"_Sketch"
    createSketch(sketchName, bodyName, 'XY_Plane', '')
    createCircleInSketch(sketchName, radius)
    createPadFromSketch(bodyName, sketchName, legHeight)
    

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
            

def createBaseCabinet(name, width, height, depth, boardThickness, cardboardThickness, sCantT, lCantT, legHeight):

    #create spreadsheet column names
    App.activeDocument().addObject('Spreadsheet::Sheet', name + "_Spreadsheet")
    spreadSheetHeaders = ['Name', 'Width', 'Height', 'BoardThickness', 'WCantFront', 'WCantBack', 'HCantLeft', 'HCantRight', 'ByFlader']
    writeRecordInSpreadsheet(name + "_Spreadsheet", spreadSheetHeaders)
    
    #create base
    bodyName = name + "_Base";
    createBody(bodyName)
    cants = [sCantT, sCantT, sCantT, sCantT]
    calcWidth = width-cants[2]-cants[3];
    calcHeight = depth-cants[0]-cants[1]-cardboardThickness
    sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, boardThickness, cants[0], cants[1], cants[2], cants[3], 0]
    row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
    createBoard(name, bodyName, row)

    #create left side
    bodyName = name + "_LeftSide"
    createBody(bodyName)
    cants = [0, sCantT, sCantT, sCantT]
    calcWidth = depth-cants[2]-cants[3]-cardboardThickness
    calcHeight = height-cants[0]-cants[1]-boardThickness-legHeight
    sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, boardThickness, cants[0], cants[1], cants[2], cants[3], 1]
    row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
    createBoard(name, bodyName, row)
    getattr(App.activeDocument(), bodyName).Placement=App.Placement(App.Vector(-width/2,0,calcHeight/2+boardThickness), App.Rotation(90,0,90), App.Vector(0,0,0))
    App.ActiveDocument.recompute()

    #create right side
    bodyName = name + "_RightSide"
    createBody(bodyName)
    cants = [sCantT, 0, sCantT, sCantT]
    calcWidth = depth-cants[2]-cants[3]-cardboardThickness
    calcHeight = height-cants[0]-cants[1]-boardThickness-legHeight
    sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, boardThickness, cants[0], cants[1], cants[2], cants[3], 1]
    row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
    createBoard(name, bodyName, row)
    getattr(App.activeDocument(), bodyName).Placement=App.Placement(App.Vector(width/2,0,calcHeight/2+boardThickness), App.Rotation(90,0,-90), App.Vector(0,0,0))
    App.ActiveDocument.recompute()

    #create front blend
    bodyName = name + "_FrontBlend";
    createBody(bodyName)
    cants = [sCantT, 0, 0, 0]
    calcWidth = width-cants[2]-cants[3]-2*boardThickness;
    calcHeight = 100
    sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, boardThickness, cants[0], cants[1], cants[2], cants[3], 0]
    row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
    createBoard(name, bodyName, row)
    getattr(App.activeDocument(), bodyName).Placement=App.Placement(App.Vector(0,-depth/2+calcHeight/2+cants[0]+cardboardThickness/2,height-legHeight-boardThickness), App.Rotation(0,0,0), App.Vector(0,0,0))
    App.ActiveDocument.recompute()

    #create back blend
    bodyName = name + "_BackBlend";
    createBody(bodyName)
    cants = [0, sCantT, 0, 0]
    calcWidth = width-cants[2]-cants[3]-2*boardThickness;
    calcHeight = 100
    sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, boardThickness, cants[0], cants[1], cants[2], cants[3], 0]
    row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
    createBoard(name, bodyName, row)
    getattr(App.activeDocument(), bodyName).Placement=App.Placement(App.Vector(0,depth/2-calcHeight/2-cants[1]-cardboardThickness/2,height-legHeight-boardThickness), App.Rotation(0,0,0), App.Vector(0,0,0))
    App.ActiveDocument.recompute()


    #create back
    bodyName = name + "_Back";
    createBody(bodyName)
    cants = [0, 0, 0, 0]
    calcWidth = width - 3;
    calcHeight = height-legHeight-3
    sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, cardboardThickness, cants[0], cants[1], cants[2], cants[3], 0]
    row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
    createBoard(name, bodyName, row)
    getattr(App.activeDocument(), bodyName).Placement=App.Placement(App.Vector(0,depth/2+cardboardThickness/2,height/2-legHeight/2), App.Rotation(0,0,90), App.Vector(0,0,0))
    App.ActiveDocument.recompute()

    # create legs
    bodyName = name + "_Leg1"
    createLeg(name, bodyName, 20, legHeight)
    getattr(App.activeDocument(), bodyName).Placement=App.Placement(App.Vector(width/3,depth/3,0), App.Rotation(0,0,180), App.Vector(0,0,0))
    App.ActiveDocument.recompute()

    bodyName = name + "_Leg2"
    createLeg(name, bodyName, 20, legHeight)
    getattr(App.activeDocument(), bodyName).Placement=App.Placement(App.Vector(-width/3,depth/3,0), App.Rotation(0,0,180), App.Vector(0,0,0))
    App.ActiveDocument.recompute()

    bodyName = name + "_Leg3"
    createLeg(name, bodyName, 20, legHeight)
    getattr(App.activeDocument(), bodyName).Placement=App.Placement(App.Vector(width/3,-depth/3,0), App.Rotation(0,0,180), App.Vector(0,0,0))
    App.ActiveDocument.recompute()

    bodyName = name + "_Leg4"
    createLeg(name, bodyName, 20, legHeight)
    getattr(App.activeDocument(), bodyName).Placement=App.Placement(App.Vector(-width/3,-depth/3,0), App.Rotation(0,0,180), App.Vector(0,0,0))
    App.ActiveDocument.recompute()

#createBaseCabinet("BottlesLeft", 300.0, 890.0, 560.0, 18.0, 3.0, 0.8, 2.0, 100.0)
