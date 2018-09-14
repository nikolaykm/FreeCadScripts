def writeRecordInSpreadsheet(spreadsheetName, recArr):
    #find next empty row
    row = 1
    while(True):
        try:
            if App.activeDocument().getObject(spreadsheetName).get('A' + str(row)) == '':
                break; 
            row = row + 1
        except ValueError:
            break

    column = ord('A')
    for item in recArr:
        App.activeDocument().getObject(spreadsheetName).set(chr(column) + str(row), str(item))
        column = column + 1

    App.ActiveDocument.recompute()

    return row

def getRowFromSpreadsheet(spreadsheetName, row):
    resultDict = dict()
    column = ord('A')
    while(True):
        try:
            key = App.activeDocument().getObject(spreadsheetName).get(chr(column) + str(1))
        except ValueError:
            break

        try:
            value = App.activeDocument().getObject(spreadsheetName).get(chr(column) + str(row))
        except ValueError:
            value = ""

        resultDict[key] = value
        column = column + 1

    return resultDict

def createBody(bodyName, objects):
    App.activeDocument().addObject('PartDesign::Body', bodyName)
    objects.append(bodyName)
    App.ActiveDocument.recompute()

def createSketch(sketchName, bodyName, supportName, supportFace):
    App.activeDocument().getObject(bodyName).newObject('Sketcher::SketchObject', sketchName)
    App.activeDocument().getObject(sketchName).Support = (App.activeDocument().getObject(supportName), [str(supportFace)])
    App.activeDocument().getObject(sketchName).MapMode = 'FlatFace'
    App.ActiveDocument.recompute()

def createRectInSketch(sketchName, xL, yL, extraConList):
    geoList = []
    geoList.append(Part.LineSegment(App.Vector(-1,1,0),App.Vector(1,1,0)))
    geoList.append(Part.LineSegment(App.Vector(1,1,0),App.Vector(1,-1,0)))
    geoList.append(Part.LineSegment(App.Vector(1,-1,0),App.Vector(-1,-1,0)))
    geoList.append(Part.LineSegment(App.Vector(-1,-1,0),App.Vector(-1,1,0)))
    App.activeDocument().getObject(sketchName).addGeometry(geoList,False)
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
    App.activeDocument().getObject(sketchName).addConstraint(conList)
    App.ActiveDocument.recompute()

def createCircleInSketch(sketchName, radius):
    App.activeDocument().getObject(sketchName).addGeometry(Part.Circle(App.Vector(0,0,0),App.Vector(0,0,1),radius),False)
    App.activeDocument().getObject(sketchName).addConstraint(Sketcher.Constraint('Coincident',0,3,-1,1))

def createLeg(cabinetName, bodyName, radius, legHeight, objects):
    createBody(bodyName, objects)
    sketchName = bodyName+"_Sketch"
    createSketch(sketchName, bodyName, 'XY_Plane', '')
    createCircleInSketch(sketchName, radius)
    createPadFromSketch(bodyName, sketchName, legHeight)
    

def createPadFromSketch(bodyName, sketchName, zL):
    padName = sketchName + "_Pad"
    App.activeDocument().getObject(bodyName).newObject("PartDesign::Pad", padName)
    App.activeDocument().getObject(padName).Profile = App.activeDocument().getObject(sketchName)
    App.activeDocument().getObject(padName).Length = zL
    App.activeDocument().getObject(padName).Length2 = 100.000000
    App.activeDocument().getObject(padName).Type = 0
    App.activeDocument().getObject(padName).UpToFace = None
    App.activeDocument().getObject(padName).Reversed = 0
    App.activeDocument().getObject(padName).Midplane = 0
    App.activeDocument().getObject(padName).Offset = 0.000000

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
            
def createCabinet(material, name, width, height, depth, addOns, boardThickness, cardboardThickness, sCantT, lCantT, legHeight, visibleBack, baseCabinetsObjects, isBase, isHavingBack = True, shiftBlend = 0.0):

    baseCabinetsObjects.append(name)

    objects = []

    #create spreadsheet column names
    App.activeDocument().addObject('Spreadsheet::Sheet', name + "_Spreadsheet")
    objects.append(name + "_Spreadsheet")
    spreadSheetHeaders = ['Name', 'Width', 'Height', 'BoardThickness', 'WCantFront', 'WCantBack', 'HCantLeft', 'HCantRight', 'ByFlader', 'Material']
    writeRecordInSpreadsheet(name + "_Spreadsheet", spreadSheetHeaders)
    
    #create base
    bodyName = name + "_Base"
    createBody(bodyName, objects)
    cants = [sCantT, sCantT if visibleBack else 0, sCantT, sCantT]
    baseCants = cants
    calcWidth = width-cants[2]-cants[3];
    calcHeight = depth-cants[0]-cants[1]-(0 if visibleBack else cardboardThickness)
    baseWidth = calcWidth
    baseHeight = calcHeight
    sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, boardThickness, cants[0], cants[1], cants[2], cants[3], 1, material]
    row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
    createBoard(name, bodyName, row)

    #create left side
    bodyName = name + "_LeftSide"
    createBody(bodyName, objects)
    cants = [0, 0 if isBase else sCantT, sCantT, sCantT if visibleBack else 0]
    calcWidth = depth-cants[2]-cants[3]-(0 if visibleBack else cardboardThickness)
    calcHeight = height-cants[0]-cants[1]-boardThickness-(legHeight if isBase else 0)
    sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, boardThickness, cants[0], cants[1], cants[2], cants[3], 1, material]
    row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
    createBoard(name, bodyName, row)
    App.activeDocument().getObject(bodyName).Placement=App.Placement(App.Vector(-width/2,0,calcHeight/2+boardThickness), App.Rotation(90,0,90), App.Vector(0,0,0))
    App.ActiveDocument.recompute()

    #create right side
    bodyName = name + "_RightSide"
    createBody(bodyName, objects)
    cants = [0 if isBase else sCantT, 0, sCantT, sCantT if visibleBack else 0]
    calcWidth = depth-cants[2]-cants[3]-(0 if visibleBack else cardboardThickness)
    calcHeight = height-cants[0]-cants[1]-boardThickness-(legHeight if isBase else 0)
    sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, boardThickness, cants[0], cants[1], cants[2], cants[3], 1, material]
    row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
    createBoard(name, bodyName, row)
    App.activeDocument().getObject(bodyName).Placement=App.Placement(App.Vector(width/2,0,calcHeight/2+boardThickness), App.Rotation(90,0,-90), App.Vector(0,0,0))
    App.ActiveDocument.recompute()
 
    if isBase:
        #create front blend
        bodyName = name + "_FrontBlend";
        createBody(bodyName, objects)
        cants = [sCantT, 0, 0, 0]
        calcWidth = width-cants[2]-cants[3]-2*boardThickness;
        calcHeight = 100
        sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, boardThickness, cants[0], cants[1], cants[2], cants[3], 0, material]
        row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
        createBoard(name, bodyName, row)
        App.activeDocument().getObject(bodyName).Placement=App.Placement(App.Vector(0,-baseHeight/2+calcHeight/2, height-legHeight-boardThickness), App.Rotation(0,0,0), App.Vector(0,0,0))
        App.ActiveDocument.recompute()

        #create back blend
        bodyName = name + "_BackBlend";
        createBody(bodyName, objects)
        cants = [0, sCantT if visibleBack else 0, 0, 0]
        calcWidth = width-cants[2]-cants[3]-2*boardThickness;
        calcHeight = 100
        sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, boardThickness, cants[0], cants[1], cants[2], cants[3], 0, material]
        row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
        createBoard(name, bodyName, row)
        App.activeDocument().getObject(bodyName).Placement=App.Placement(App.Vector(0,baseHeight/2-calcHeight/2, height-legHeight-boardThickness), App.Rotation(0,0,0), App.Vector(0,0,0))
        App.ActiveDocument.recompute()

    else:
        #create whole blend
        bodyName = name + "_WholeBlend";
        createBody(bodyName, objects)
        cants = [sCantT, 0, 0, 0]
        calcWidth = width-cants[2]-cants[3]-2*boardThickness;
        calcHeight = baseHeight
        sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, boardThickness, cants[0], cants[1], cants[2], cants[3], 0, material]
        row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
        createBoard(name, bodyName, row)
        App.activeDocument().getObject(bodyName).Placement=App.Placement(App.Vector(0,0, height-boardThickness-shiftBlend), App.Rotation(0,0,0), App.Vector(0,0,0))
        App.ActiveDocument.recompute()
    
    if isHavingBack:  
        bodyName = name + "_Back";
        createBody(bodyName, objects)
        cants = [0, 0, 0, 0]

    if not visibleBack:
        #create back from cardboard
        calcWidth = width - 3;
        calcHeight = height-(legHeight if isBase else 0)-3
        sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, cardboardThickness, cants[0], cants[1], cants[2], cants[3], 0, material+"_card"]
        row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
        createBoard(name, bodyName, row)
        App.activeDocument().getObject(bodyName).Placement=App.Placement(App.Vector(0,baseHeight/2+cardboardThickness,height/2-(legHeight if isBase else 0)/2), App.Rotation(0,0,90), App.Vector(0,0,0))
        App.ActiveDocument.recompute()
    else:
        if isHavingBack:
            #create back from normal board
            calcWidth = width-cants[2]-cants[3]-2*boardThickness;
            calcHeight = height-(legHeight if isBase else 0)-cants[0]-cants[1]-2*boardThickness
            sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, boardThickness, cants[0], cants[1], cants[2], cants[3], 1, material]
            row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
            createBoard(name, bodyName, row)
            App.activeDocument().getObject(bodyName).Placement=App.Placement(App.Vector(0,baseHeight/2+baseCants[1],height/2-(legHeight if isBase else 0)/2), App.Rotation(0,0,90), App.Vector(0,0,0))
            App.ActiveDocument.recompute()

    if isBase:
        # create legs
        signW = -1
        signH = 1
        for legNum in range(1,5):
            bodyName = name + "_Leg" + str(legNum)
            createLeg(name, bodyName, 20, legHeight, objects)
            signW = signW * (-1 if legNum%2==1 else 1)
            signH = signH * (1 if legNum%2==1 else -1)
            legWidth = (width/3)*signW
            legDepth = (depth/3)*signH
            App.activeDocument().getObject(bodyName).Placement=App.Placement(App.Vector(legWidth,legDepth,0), App.Rotation(0,0,180), App.Vector(0,0,0))
            App.ActiveDocument.recompute()

    #create addOns
    for addOn in addOns:
        bodyName = name + addOn[0]
        createBody(bodyName, objects)
        cants = addOn[3]
        calcWidth = addOn[1] - cants[2] - cants[3]
        calcHeight = addOn[2] - cants[0] - cants[1]
        sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, boardThickness, cants[0], cants[1], cants[2], cants[3], 1, material]
        row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
        createBoard(name, bodyName, row)
        App.activeDocument().getObject(bodyName).Placement=App.Placement(App.Vector(addOn[4],(-baseHeight/2-baseCants[0]-2) if addOn[7] else addOn[5], ((height/2 - (legHeight if isBase else 0)/2) if addOn[7] else 0) + addOn[6]), App.Rotation(0,0,(90 if addOn[7] else 0)), App.Vector(0,0,0))
        App.ActiveDocument.recompute()

    App.activeDocument().addObject("Part::MultiFuse",name + "_Fusion")
    objectsFreeCad = []
    for objName in objects:
        objectsFreeCad.append(App.activeDocument().getObject(objName))

    App.activeDocument().getObject(name + "_Fusion").Shapes = objectsFreeCad

    App.ActiveDocument.recompute()

def createDrawer(material, name, width, height, depth, boardThickness, cardboardThickness, sCantT, lCantT, drawersObjects, visibleBack):
    drawersObjects.append(name)

    objects = []

    #create spreadsheet column names
    App.activeDocument().addObject('Spreadsheet::Sheet', name + "_Spreadsheet")
    objects.append(name + "_Spreadsheet")
    spreadSheetHeaders = ['Name', 'Width', 'Height', 'BoardThickness', 'WCantFront', 'WCantBack', 'HCantLeft', 'HCantRight', 'ByFlader', 'Material']
    writeRecordInSpreadsheet(name + "_Spreadsheet", spreadSheetHeaders)

    #create base
    bodyName = name + "_Base"
    createBody(bodyName, objects)
    cants = [0, 0, 0, 0]
    calcWidth = width-cants[2]-cants[3]-4*boardThickness+6;
    calcHeight = depth-cants[2]-cants[3]-(boardThickness if visibleBack else cardboardThickness)-5
    sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, cardboardThickness, cants[0], cants[1], cants[2], cants[3], 1, material+"_card"]
    row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
    createBoard(name, bodyName, row)
    App.activeDocument().getObject(bodyName).Placement=App.Placement(App.Vector(0,0,-(height-cants[0]-cants[1]-2*30)/2-cardboardThickness+20), App.Rotation(0,0,0), App.Vector(0,0,0))
    App.ActiveDocument.recompute()

    #create left side
    bodyName = name + "_LeftSide"
    createBody(bodyName, objects)
    cants = [sCantT, sCantT, 0, sCantT]
    calcWidth = depth-cants[2]-cants[3]-(boardThickness if visibleBack else cardboardThickness)-5
    calcHeight = height-cants[0]-cants[1]-2*30
    sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, boardThickness, cants[0], cants[1], cants[2], cants[3], 1, material]
    row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
    createBoard(name, bodyName, row)
    App.activeDocument().getObject(bodyName).Placement=App.Placement(App.Vector(-width/2+boardThickness+5,0,0), App.Rotation(90,0,90), App.Vector(0,0,0))
    App.ActiveDocument.recompute()

    #create right side
    bodyName = name + "_RightSide"
    createBody(bodyName, objects)
    cants = [sCantT, sCantT, 0, sCantT]
    calcWidth = depth-cants[2]-cants[3]-(boardThickness if visibleBack else cardboardThickness)-5
    calcHeight = height-cants[0]-cants[1]-2*30
    sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, boardThickness, cants[0], cants[1], cants[2], cants[3], 1, material]
    row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
    createBoard(name, bodyName, row)
    App.activeDocument().getObject(bodyName).Placement=App.Placement(App.Vector(width/2-boardThickness-5,0,0), App.Rotation(90,0,-90), App.Vector(0,0,0))
    App.ActiveDocument.recompute()

    #create back
    bodyName = name + "_Back"
    createBody(bodyName, objects)
    cants = [sCantT, sCantT, 0, 0]
    calcWidth = width-cants[2]-cants[3]-4*boardThickness-10
    calcHeight = height-cants[0]-cants[1]-2*30 - 20
    sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, boardThickness, cants[0], cants[1], cants[2], cants[3], 1, material]
    row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
    createBoard(name, bodyName, row)
    App.activeDocument().getObject(bodyName).Placement=App.Placement(App.Vector(0,(depth+sCantT-(boardThickness if visibleBack else cardboardThickness)-5)/2, 10), App.Rotation(0,0,90), App.Vector(0,0,0))
    App.ActiveDocument.recompute()

    #create front
    bodyName = name + "_Front"
    createBody(bodyName, objects)
    cants = [sCantT, sCantT, 0, 0]
    calcWidth = width-cants[2]-cants[3]-4*boardThickness-10;
    calcHeight = height-cants[0]-cants[1]-2*30 - 20
    sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, boardThickness, cants[0], cants[1], cants[2], cants[3], 1, material]
    row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
    createBoard(name, bodyName, row)
    App.activeDocument().getObject(bodyName).Placement=App.Placement(App.Vector(0,-(depth-sCantT-3*(boardThickness if visibleBack else cardboardThickness)-5)/2, 10), App.Rotation(0,0,90), App.Vector(0,0,0))
    App.ActiveDocument.recompute()

    #create door
    bodyName = name + "_Door"
    createBody(bodyName, objects)
    cants = [lCantT, lCantT, lCantT, lCantT]
    calcWidth = width-cants[2]-cants[3]-3;
    calcHeight = height-cants[0]-cants[1]-3
    sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, boardThickness, cants[0], cants[1], cants[2], cants[3], 1, material]
    row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
    createBoard(name, bodyName, row)
    App.activeDocument().getObject(bodyName).Placement=App.Placement(App.Vector(0,-(depth-sCantT-(boardThickness if visibleBack else cardboardThickness)-5)/2, 10), App.Rotation(0,0,90), App.Vector(0,0,0))
    App.ActiveDocument.recompute()



    App.activeDocument().addObject("Part::MultiFuse",name + "_Fusion")
    objectsFreeCad = []
    for objName in objects:
        objectsFreeCad.append(App.activeDocument().getObject(objName))

    App.activeDocument().getObject(name + "_Fusion").Shapes = objectsFreeCad

    App.ActiveDocument.recompute()


 

def createPlot(material, name, plotName, width, plotObjects):
    bodyName = name + plotName
    createBody(bodyName, plotObjects)
    cants = [0, 0, 0, 0]
    calcWidth = width
    calcHeight = 600
    sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, 40, cants[0], cants[1], cants[2], cants[3], 0, material]
    row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
    createBoard(name, bodyName, row)

def createPlotBack(material, name, plotBackName, width, height, plotBackObjects, cants, boardThickness):
    bodyName = name + plotBackName
    createBody(bodyName, plotBackObjects)
    calcWidth = width - cants[2] - cants[3]
    calcHeight = height - cants[0] - cants[1]
    sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, boardThickness, cants[0], cants[1], cants[2], cants[3], 0, material]
    row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
    createBoard(name, bodyName, row)


def createBaseCorpuses(height):
    #creating base corpuses
    baseCabinetsObjects = []

    addOns = [["Door1", 297.0, height-103.0, [2, 2, 2, 2], 0, 0, 0, True]]
    createCabinet('WallnutTropic', 'Bottles', 300.0, height, 560.0, addOns, 18.0, 3.0, 0.8, 2.0, 100.0, False, baseCabinetsObjects, True)
    App.ActiveDocument.getObject('Bottles_Fusion').Placement = App.Placement(App.Vector(-1316,-402,100),App.Rotation(App.Vector(0,0,1),0))

    addOns = [["Shelf1", 564.0, 526.2, [0.8, 0, 0, 0], 0, -15.40, 122.0, False], 
              ["Door1", 597.0, 137.0, [2, 2, 2, 2], 0, 0, -309.5, True]]
    createCabinet('WallnutTropic', 'Oven', 600.0, height, 560.0, addOns, 18.0, 3.0, 0.8, 2.0, 100.0, False, baseCabinetsObjects, True)
    App.ActiveDocument.getObject('Oven_Fusion').Placement = App.Placement(App.Vector(-1766,-402,100),App.Rotation(App.Vector(0,0,1),0))

    addOns = [["Shelf1", 1184.0, 496.2, [0.8, 0, 0, 0], 0, 0.4, 350.0, False],
              ["Plank1", 100.0, height-103.0, [0,0,0,0], -557, 0, 0, True],
              ["Plank2", 197.0, height-103.0, [2,2,0,2], -90, 0, 0, True], 
              ["Door1", 597.0, height-103.0, [2,2,2,2], 310, 0, 0, True]]
    createCabinet('WallnutTropic', 'Cab1', 1220.0, height, 500.0, addOns, 18.0, 3.0, 0.8, 2.0, 100.0, False, baseCabinetsObjects, True)
    App.ActiveDocument.getObject('Cab1_Fusion').Placement = App.Placement(App.Vector(-3276,-432,100),App.Rotation(App.Vector(0,0,1),0))

    addOns = [["Shelf1", 406.0, 506.2, [0.8, 0, 0, 0], 0, 0.4, 350.0, False],
              ["Door1", 439.0, height-103.0, [2, 2, 2, 2], 0, 0, 0, True]]
    createCabinet('WallnutTropic', 'Cab2', 442.0, height, 510.0, addOns, 18.0, 3.0, 0.8, 2.0, 100.0, False, baseCabinetsObjects, True)
    App.ActiveDocument.getObject('Cab2_Fusion').Placement = App.Placement(App.Vector(-3630,-922,100),App.Rotation(App.Vector(0,0,1),90))

    addOns = [["Door1", 597.0, height-103.0, [2, 2, 2, 2], 0, 0, 0, True]]
    createCabinet('WallnutTropic', 'Sink', 600.0, height, 560.0, addOns, 18.0, 3.0, 0.8, 2.0, 100.0, False, baseCabinetsObjects, True)
    App.ActiveDocument.getObject('Sink_Fusion').Placement = App.Placement(App.Vector(-3655,-1443,100),App.Rotation(App.Vector(0,0,1),90))

    addOns = [["Shelf1", 1054.0, 366.2, [0.8, 0, 0, 0], 0, 0.4, 350.0, False],
              ["Plank1", 100.0, height-103.0, [0,0,0,0], 492, 0, 0, True],
              ["Plank2", 197.0, height-103.0, [2,2,2,0], 7.5, 0, 0, True], 
              ["Door1", 450.0, height-103.0, [2,2,2,2], -318.5, 0, 0, True]]
    createCabinet('WallnutTropic', 'Cab3', 1090.0, height, 370.0, addOns, 18.0, 3.0, 0.8, 2.0, 100.0, False, baseCabinetsObjects, True)
    App.ActiveDocument.getObject('Cab3_Fusion').Placement = App.Placement(App.Vector(-3391,-1947,100),App.Rotation(App.Vector(0,0,1),180))
 
    addOns = []
    createCabinet('WallnutTropic', 'Cab4', 600.0, height, 560.0, addOns, 18.0, 3.0, 0.8, 2.0, 100.0, True, baseCabinetsObjects, True)
    App.ActiveDocument.getObject('Cab4_Fusion').Placement = App.Placement(App.Vector(-2546,-2043,100),App.Rotation(App.Vector(0,0,1),180))

    addOns = [["Shelf1", 932.0, 541.2, [0.8, 0, 0, 0], 0, -9, 350.0, False],
              ["Door1", 481.0, height-103.0, [2,2,2,2], -242, 0, 0, True],
              ["Door2", 481.0, height-103.0, [2,2,2,2], 242, 0, 0, True]]
    createCabinet('WallnutTropic', 'Cab5', 968.0, height, 560.0, addOns, 18.0, 3.0, 0.8, 2.0, 100.0, True, baseCabinetsObjects, True)
    App.ActiveDocument.getObject('Cab5_Fusion').Placement = App.Placement(App.Vector(-1762,-2043,100),App.Rotation(App.Vector(0,0,1),180))



    App.ActiveDocument.addObject("App::DocumentObjectGroup","BaseCabinets")
    for obj in baseCabinetsObjects:
        App.ActiveDocument.getObject("BaseCabinets").addObject(App.ActiveDocument.getObject(obj+"_Fusion"))

def createUpCorpuses(height, depth):
    #creating up corpuses
    upCabinetsObjects = []

    addOns = [["Shelf1", 264.0, depth-3-0.8, [0.8, 0, 0, 0], 0, 0.4, 350.0, False],
              ["Door1", 297.0, height-253-3, [2, 2, 2, 2], 0, 0, 0, True]]
    createCabinet('WallnutTropic', 'BottlesUp', 300.0, height-253.0, depth, addOns, 18.0, 3.0, 0.8, 2.0, 100.0, False, upCabinetsObjects, False)
    App.ActiveDocument.getObject('BottlesUp_Fusion').Placement = App.Placement(App.Vector(-1316,-266,2197),App.Rotation(App.Vector(0,1,0),180))

    addOns = [["Shelf1", 564.0, depth-3-0.8, [0.8, 0, 0, 0], 0, 0.4, 350.0, False],
              ["Door1", 597.0, height-40-3, [2, 2, 2, 2], 0, 0, 0, True]]
    createCabinet('WallnutTropic', 'OvenUp', 600.0, height-40, depth, addOns, 18.0, 3.0, 0.8, 2.0, 100.0, False, upCabinetsObjects, False, True, 220.0)
    App.ActiveDocument.getObject('OvenUp_Fusion').Placement = App.Placement(App.Vector(-1766,-266,2450),App.Rotation(App.Vector(0,1,0),180))

    addOns = [["Shelf1", 1124.0, depth-3-0.8, [0.8, 0, 0, 0], 0, 0.4, 350.0, False],
              ["Shelf2", 1124.0, depth-3-0.8, [0.8, 0, 0, 0], 0, 0.4, 672.0, False],
              ["Door1", 577.0, height-3, [2,2,2,2], -290, 0, 0, True],
              ["Door2", 577.0, height-3, [2,2,2,2], 290, 0, 0, True]]
    createCabinet('WallnutTropic', 'Cab1Up', 1160.0, height, depth, addOns, 18.0, 3.0, 0.8, 2.0, 100.0, False, upCabinetsObjects, False)
    App.ActiveDocument.getObject('Cab1Up_Fusion').Placement = App.Placement(App.Vector(-2646,-266,2450),App.Rotation(App.Vector(0,1,0),180))

    addOns = [["Door1", 697.0, height+200-3, [2, 2, 2, 2], 0, 0, 0, True]]
    createCabinet('WallnutTropic', 'Cab2Up', 700.0, height+200, 480.0, addOns, 18.0, 3.0, 0.8, 2.0, 100.0, True, upCabinetsObjects, False, False)
    App.ActiveDocument.getObject('Cab2Up_Fusion').Placement = App.Placement(App.Vector(-3577,-373,2450),App.Rotation(App.Vector(0,1,0),180))

    addOns = [["Shelf1", 564.0, 250-3-0.8, [0.8, 0, 0, 0], 0, 0.4, 350.0, False],
              ["Shelf2", 564.0, 250-3-0.8, [0.8, 0, 0, 0], 0, 0.4, 672.0, False],
              ["Door1", 597.0, height-3, [2,2,2,2], 0, 0, 0, True]]
    createCabinet('WallnutTropic', 'Cab3Up', 600.0, height, 250.0, addOns, 18.0, 3.0, 0.8, 2.0, 100.0, False, upCabinetsObjects, False)
    App.ActiveDocument.getObject('Cab3Up_Fusion').Placement = App.Placement(App.Vector(-3160,-2019,1500),App.Rotation(App.Vector(0,0,1),180))

    App.ActiveDocument.addObject("App::DocumentObjectGroup","UpCabinets")
    for obj in upCabinetsObjects:
        App.ActiveDocument.getObject("UpCabinets").addObject(App.ActiveDocument.getObject(obj+"_Fusion"))


def createPlots(height):
    #create plots
    name = "Plots"
    plotObjects = []

    #create spreadsheet column names
    App.activeDocument().addObject('Spreadsheet::Sheet', name + "_Spreadsheet")
    plotObjects.append(name + "_Spreadsheet")
    spreadSheetHeaders = ['Name', 'Width', 'Height', 'BoardThickness', 'WCantFront', 'WCantBack', 'HCantLeft', 'HCantRight', 'ByFlader', 'Material']
    writeRecordInSpreadsheet(name + "_Spreadsheet", spreadSheetHeaders)

    plotProperties = []
    plotProperties.append(["_Right", 2172.0, App.Placement(App.Vector(-2252,-420,height-40), App.Rotation(0,0,0), App.Vector(0,0,0))])
    plotProperties.append(["_Front", 2020.0, App.Placement(App.Vector(-3640,-1130,height-40), App.Rotation(App.Vector(0,0,1),90))])
    plotProperties.append(["_Left", 2060.0, App.Placement(App.Vector(-2308,-2023,height-40), App.Rotation(0,0,0), App.Vector(0,0,0))])

    for plotProp in plotProperties:
        createPlot('PlotsGranite', name, plotProp[0], plotProp[1], plotObjects)
        App.activeDocument().getObject(name+plotProp[0]).Placement=plotProp[2]
    App.ActiveDocument.recompute()

    App.ActiveDocument.addObject("App::DocumentObjectGroup","Plots")
    for obj in plotObjects:
        App.ActiveDocument.getObject("Plots").addObject(App.ActiveDocument.getObject(obj))

def createBackForPlots(height):
    #create backs for plots
    name = "PlotsBacks"
    plotObjects = []

    #create spreadsheet column names
    App.activeDocument().addObject('Spreadsheet::Sheet', name + "_Spreadsheet")
    plotObjects.append(name + "_Spreadsheet")
    spreadSheetHeaders = ['Name', 'Width', 'Height', 'BoardThickness', 'WCantFront', 'WCantBack', 'HCantLeft', 'HCantRight', 'ByFlader', 'Material']
    writeRecordInSpreadsheet(name + "_Spreadsheet", spreadSheetHeaders)

    plotProperties = []
    plotProperties.append(["_Right1", 2100.0, height, App.Placement(App.Vector(-2216,-115,1200),App.Rotation(App.Vector(1,0,0),90)), [0.8, 0.8, 0.8, 0.8]])
    plotProperties.append(["_Right2", 80.0, 400.0, App.Placement(App.Vector(-3245,-173,1100), App.Rotation(90,0,90), App.Vector(0,0,0)), [0.8, 0.8, 0.8, 0.8]])
    plotProperties.append(["_Front1", 70.0, height, App.Placement(App.Vector(-3945,-2110,1200), App.Rotation(90,0,90), App.Vector(0,0,0)), [0.8, 0.8, 0.8, 0.8]])
    plotProperties.append(["_Front2", 1320.0, 115.0, App.Placement(App.Vector(-3945,-1415,957), App.Rotation(90,0,90), App.Vector(0,0,0)), [0.8, 0.8, 0.8, 0.8]])
    plotProperties.append(["_Front3", 620.0, height, App.Placement(App.Vector(-3945,-445,1200), App.Rotation(90,0,90), App.Vector(0,0,0)), [0.8, 0.8, 0.8, 0.8]])
    plotProperties.append(["_Left1", 1072.0, height, App.Placement(App.Vector(-3391,-2127,1200),App.Rotation(App.Vector(1,0,0),90)), [0.8, 0.8, 0.8, 0.8]])
    plotProperties.append(["_Left2", 203.0, height, App.Placement(App.Vector(-2855,-2229,1200), App.Rotation(90,0,90), App.Vector(0,0,0)), [0.8, 0.8, 0.8, 0.8]])
    plotProperties.append(["_Left3", 1559.0, 400.0, App.Placement(App.Vector(-2058,-2312,1100),App.Rotation(App.Vector(1,0,0),90)), [0.8, 0.8, 0.8, 0.8]])
    #TODO:Add window plots back

    for plotProp in plotProperties:
        createPlotBack('DecoriniQuadrs',name, plotProp[0], plotProp[1], plotProp[2], plotObjects, plotProp[4], 18)
        App.activeDocument().getObject(name+plotProp[0]).Placement=plotProp[3]
    App.ActiveDocument.recompute()

    App.ActiveDocument.addObject("App::DocumentObjectGroup","PlotsBacks")
    for obj in plotObjects:
        App.ActiveDocument.getObject("PlotsBacks").addObject(App.ActiveDocument.getObject(obj))



#create Vitodens 111-W with fux
def createVitodens():

    #create spreadsheet column names
    App.activeDocument().addObject('Spreadsheet::Sheet', "Vitodens_Spreadsheet")
    spreadSheetHeaders = ['Name', 'Width', 'Height', 'BoardThickness', 'WCantFront', 'WCantBack', 'HCantLeft', 'HCantRight', 'ByFlader']
    writeRecordInSpreadsheet("Vitodens_Spreadsheet", spreadSheetHeaders)

    bodyName = "Vitodens_111W"
    createBody(bodyName, [])
    cants = [0, 0, 0, 0]
    calcWidth = 600.0
    calcHeight = 480.0
    sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, 1060.0, cants[0], cants[1], cants[2], cants[3], 0]
    row = writeRecordInSpreadsheet("Vitodens_Spreadsheet", sprRec)
    createBoard("Vitodens", "Vitodens_111W", row)

    App.activeDocument().getObject("Vitodens_111W").Placement = App.Placement(App.Vector(-3600,-355,1000), App.Rotation(0,0,0), App.Vector(0,0,0))

    App.ActiveDocument.addObject("App::DocumentObjectGroup","Vitodens")
    App.ActiveDocument.getObject("Vitodens").addObject(App.ActiveDocument.getObject("Vitodens_Spreadsheet"))
    App.ActiveDocument.getObject("Vitodens").addObject(App.ActiveDocument.getObject("Vitodens_111W"))

def createLivingRoomCorpuses():
    #creating up corpuses
    livingRoomObjects = []

    addOns = []
    #addOns = [["Shelf1", 264.0, depth-3-0.8, [0.8, 0, 0, 0], 0, 0.4, 350.0, False],
    #          ["Door1", 297.0, height-253-3, [2, 2, 2, 2], 0, 0, 0, True]]
    createCabinet('WallnutTropic', 'LivingRoomCab1', 450.0, 1800.0, 450.0, addOns, 18.0, 3.0, 0.8, 2.0, 100.0, False, livingRoomObjects, True)
    App.ActiveDocument.getObject('LivingRoomCab1_Fusion').Placement = App.Placement(App.Vector(504.0,-346.0,0),App.Rotation(App.Vector(0,0,0),0))

    App.ActiveDocument.addObject("App::DocumentObjectGroup","LivingRoomCabinets")
    for obj in livingRoomObjects:
        App.ActiveDocument.getObject("LivingRoomCabinets").addObject(App.ActiveDocument.getObject(obj+"_Fusion"))

def processAllSpreadSheetsByMaterial():
    finalDict = dict()
    allSpreadSheets = App.ActiveDocument.findObjects('Spreadsheet::Sheet')
    for item in allSpreadSheets:
        rowDict = getRowFromSpreadsheet(item.Name, 0)
        if 'Material' in rowDict:
            print "Processing ... " + item.Name
            curRow = 1
            while True:
                curRowDict = getRowFromSpreadsheet(item.Name, curRow)
                if curRowDict['Name'] == '': break
                #print curRowDict
                curRow = curRow + 1

                if curRowDict['Material'] not in finalDict:
                    curRowDict['Count'] = 1
                    finalDict[curRowDict['Material']] = []
                    finalDict[curRowDict['Material']].append(curRowDict)
                else:
                    found = False
                    for x in finalDict[curRowDict['Material']]:
                       if x['Height'] == curRowDict['Height'] and \
                          x['Width'] == curRowDict['Width'] and \
                          x['HCantRight']+x['HCantLeft'] == curRowDict['HCantRight']+curRowDict['HCantLeft'] and \
                          x['BoardThickness'] == curRowDict['BoardThickness'] and \
                          x['WCantFront']+x['WCantBack'] == curRowDict['WCantFront']+curRowDict['WCantBack'] and \
                          x['ByFlader'] == curRowDict['ByFlader']:
                           x['Count'] = x['Count'] + 1
                           found = True
                           break
                    if not found:
                        curRowDict['Count'] = 1
                        finalDict[curRowDict['Material']].append(curRowDict)

    for mat in finalDict:
        #create spreadsheet column names
        App.activeDocument().addObject('Spreadsheet::Sheet', mat + "_Spreadsheet")
        spreadSheetHeaders = ['Width', 'Height', 'WCantFront', 'WCantBack', 'HCantLeft', 'HCantRight', 'ByFlader', 'Count']
        writeRecordInSpreadsheet(mat + "_Spreadsheet", spreadSheetHeaders)

        for x in finalDict[mat]:
            row = [x['Width'], x['Height'], x['WCantFront'], x['WCantBack'], x['HCantLeft'], x['HCantRight'], x['ByFlader'], x['Count']]
            writeRecordInSpreadsheet(mat + "_Spreadsheet", row)
                    

#createBaseCorpuses(860.0)
#createPlots(900)
#createVitodens()
#createBackForPlots(600.0)
#createUpCorpuses(950.0, 300.0)
#createLivingRoomCorpuses()
#processAllSpreadSheetsByMaterial()
#drawersObjects = []
#createDrawer('WallnutTropic','Cab1_Drawer1', 600.0, 187.0, 560.0, 18.0, 3.0, 0.8, 2.0, drawersObjects, True)

#execfile('/home/nm/Dev/FreeCadScripts/createBaseCorpus.py')
