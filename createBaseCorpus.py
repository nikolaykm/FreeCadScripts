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
            
def createCabinet(name, width, height, depth, boardThickness, cardboardThickness, sCantT, lCantT, legHeight, visibleBack, baseCabinetsObjects, isBase):

    baseCabinetsObjects.append(name)

    objects = []

    #create spreadsheet column names
    App.activeDocument().addObject('Spreadsheet::Sheet', name + "_Spreadsheet")
    objects.append(name + "_Spreadsheet")
    spreadSheetHeaders = ['Name', 'Width', 'Height', 'BoardThickness', 'WCantFront', 'WCantBack', 'HCantLeft', 'HCantRight', 'ByFlader']
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
    sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, boardThickness, cants[0], cants[1], cants[2], cants[3], 1]
    row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
    createBoard(name, bodyName, row)

    #create left side
    bodyName = name + "_LeftSide"
    createBody(bodyName, objects)
    cants = [0, 0, sCantT, sCantT if visibleBack else 0]
    calcWidth = depth-cants[2]-cants[3]-(0 if visibleBack else cardboardThickness)
    calcHeight = height-cants[0]-cants[1]-boardThickness-(legHeight if isBase else 0)
    sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, boardThickness, cants[0], cants[1], cants[2], cants[3], 1]
    row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
    createBoard(name, bodyName, row)
    App.activeDocument().getObject(bodyName).Placement=App.Placement(App.Vector(-width/2,0,calcHeight/2+boardThickness), App.Rotation(90,0,90), App.Vector(0,0,0))
    App.ActiveDocument.recompute()

    #create right side
    bodyName = name + "_RightSide"
    createBody(bodyName, objects)
    cants = [0, 0, sCantT, sCantT if visibleBack else 0]
    calcWidth = depth-cants[2]-cants[3]-(0 if visibleBack else cardboardThickness)
    calcHeight = height-cants[0]-cants[1]-boardThickness-(legHeight if isBase else 0)
    sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, boardThickness, cants[0], cants[1], cants[2], cants[3], 1]
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
        sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, boardThickness, cants[0], cants[1], cants[2], cants[3], 0]
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
        sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, boardThickness, cants[0], cants[1], cants[2], cants[3], 0]
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
        sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, boardThickness, cants[0], cants[1], cants[2], cants[3], 0]
        row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
        createBoard(name, bodyName, row)
        App.activeDocument().getObject(bodyName).Placement=App.Placement(App.Vector(0,0, height-boardThickness), App.Rotation(0,0,0), App.Vector(0,0,0))
        App.ActiveDocument.recompute()
      
    bodyName = name + "_Back";
    createBody(bodyName, objects)
    cants = [0, 0, 0, 0]

    if not visibleBack:
        #create back from cardboard
        calcWidth = width - 3;
        calcHeight = height-(legHeight if isBase else 0)-3
        sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, cardboardThickness, cants[0], cants[1], cants[2], cants[3], 0]
        row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
        createBoard(name, bodyName, row)
        App.activeDocument().getObject(bodyName).Placement=App.Placement(App.Vector(0,baseHeight/2+cardboardThickness,height/2-(legHeight if isBase else 0)/2), App.Rotation(0,0,90), App.Vector(0,0,0))
        App.ActiveDocument.recompute()
    else:
        #create back from normal board
        calcWidth = width-cants[2]-cants[3]-2*boardThickness;
        calcHeight = height-(legHeight if isBase else 0)-cants[0]-cants[1]-2*boardThickness
        sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, boardThickness, cants[0], cants[1], cants[2], cants[3], 1]
        row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
        createBoard(name, bodyName, row)
        App.activeDocument().getObject(bodyName).Placement=App.Placement(App.Vector(0,baseHeight/2+baseCants[1],height/2-(legHeight if isBase else 0)/2), App.Rotation(0,0,90), App.Vector(0,0,0))
        App.ActiveDocument.recompute()
        pass

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

    App.activeDocument().addObject("Part::MultiFuse",name + "_Fusion")
    objectsFreeCad = []
    for objName in objects:
        objectsFreeCad.append(App.activeDocument().getObject(objName))

    App.activeDocument().getObject(name + "_Fusion").Shapes = objectsFreeCad

    App.ActiveDocument.recompute()

def createPlot(name, plotName, width, plotObjects):
    bodyName = name + plotName
    createBody(bodyName, plotObjects)
    cants = [0, 0, 0, 0]
    calcWidth = width
    calcHeight = 600
    sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, 40, cants[0], cants[1], cants[2], cants[3], 0]
    row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
    createBoard(name, bodyName, row)

def createPlotBack(name, plotBackName, width, height, plotBackObjects, sCantT, boardThickness):
    bodyName = name + plotBackName
    createBody(bodyName, plotBackObjects)
    cants = [0, 0, sCantT, sCantT]
    calcWidth = width
    calcHeight = height
    sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, boardThickness, cants[0], cants[1], cants[2], cants[3], 0]
    row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
    createBoard(name, bodyName, row)


def createBaseCorpuses(height):
    #creating base corpuses
    baseCabinetsObjects = []
    createCabinet('Bottles', 300.0, height, 560.0, 18.0, 3.0, 0.8, 2.0, 100.0, False, baseCabinetsObjects, True)
    App.ActiveDocument.getObject('Bottles_Fusion').Placement = App.Placement(App.Vector(-1312,-402,100),App.Rotation(App.Vector(0,0,1),0))
    createCabinet('Oven', 600.0, height, 560.0, 18.0, 3.0, 0.8, 2.0, 100.0, False, baseCabinetsObjects, True)
    App.ActiveDocument.getObject('Oven_Fusion').Placement = App.Placement(App.Vector(-1762,-402,100),App.Rotation(App.Vector(0,0,1),0))
    ##createCabinet('Dishwasher', 600.0, height, 560.0, 18.0, 3.0, 0.8, 2.0, 100.0, False, baseCabinetsObjects, True)
    ##App.ActiveDocument.getObject('Dishwasher_Fusion').Placement = App.Placement(App.Vector(-2362,-402,100),App.Rotation(App.Vector(0,0,1),0))
    createCabinet('Cab1', 1220.0, height, 500.0, 18.0, 3.0, 0.8, 2.0, 100.0, False, baseCabinetsObjects, True)
    App.ActiveDocument.getObject('Cab1_Fusion').Placement = App.Placement(App.Vector(-3272,-432,100),App.Rotation(App.Vector(0,0,1),0))
    createCabinet('Cab2', 482.0, height, 520.0, 18.0, 3.0, 0.8, 2.0, 100.0, False, baseCabinetsObjects, True)
    App.ActiveDocument.getObject('Cab2_Fusion').Placement = App.Placement(App.Vector(-3630,-922,100),App.Rotation(App.Vector(0,0,1),90))
    createCabinet('Sink', 600.0, height, 560.0, 18.0, 3.0, 0.8, 2.0, 100.0, False, baseCabinetsObjects, True)
    App.ActiveDocument.getObject('Sink_Fusion').Placement = App.Placement(App.Vector(-3655,-1463,100),App.Rotation(App.Vector(0,0,1),90))
    createCabinet('Cab3', 1090.0, height, 370.0, 18.0, 3.0, 0.8, 2.0, 100.0, False, baseCabinetsObjects, True)
    App.ActiveDocument.getObject('Cab3_Fusion').Placement = App.Placement(App.Vector(-3391,-1947,100),App.Rotation(App.Vector(0,0,1),180))
    createCabinet('Cab4', 492.0, height, 560.0, 18.0, 3.0, 0.8, 2.0, 100.0, True, baseCabinetsObjects, True)
    App.ActiveDocument.getObject('Cab4_Fusion').Placement = App.Placement(App.Vector(-2600,-2043,100),App.Rotation(App.Vector(0,0,1),180))
    createCabinet('Cab5', 492.0, height, 560.0, 18.0, 3.0, 0.8, 2.0, 100.0, True, baseCabinetsObjects, True)
    App.ActiveDocument.getObject('Cab5_Fusion').Placement = App.Placement(App.Vector(-2108,-2043,100),App.Rotation(App.Vector(0,0,1),180))
    createCabinet('Cab6', 600.0, height, 560.0, 18.0, 3.0, 0.8, 2.0, 100.0, True, baseCabinetsObjects, True)
    App.ActiveDocument.getObject('Cab6_Fusion').Placement = App.Placement(App.Vector(-1562,-2043,100),App.Rotation(App.Vector(0,0,1),180))

    App.ActiveDocument.addObject("App::DocumentObjectGroup","BaseCabinets")
    for obj in baseCabinetsObjects:
        App.ActiveDocument.getObject("BaseCabinets").addObject(App.ActiveDocument.getObject(obj+"_Fusion"))

def createUpCorpuses(height):
    #creating up corpuses
    upCabinetsObjects = []
    createCabinet('BottlesUp', 300.0, height-238.0, 300.0, 18.0, 3.0, 0.8, 2.0, 100.0, False, upCabinetsObjects, False)
    App.ActiveDocument.getObject('BottlesUp_Fusion').Placement = App.Placement(App.Vector(-1312,-266,1530),App.Rotation(App.Vector(0,0,1),0))
    createCabinet('OvenUp', 600.0, height, 300.0, 18.0, 3.0, 0.8, 2.0, 100.0, False, upCabinetsObjects, False)
    App.ActiveDocument.getObject('OvenUp_Fusion').Placement = App.Placement(App.Vector(-1762,-266,1530),App.Rotation(App.Vector(0,0,1),0))

    createCabinet('Cab1Up', 1183.0, height, 300.0, 18.0, 3.0, 0.8, 2.0, 100.0, False, upCabinetsObjects, False)
    App.ActiveDocument.getObject('Cab1Up_Fusion').Placement = App.Placement(App.Vector(-2654,-266,1530),App.Rotation(App.Vector(0,0,1),0))

    App.ActiveDocument.addObject("App::DocumentObjectGroup","UpCabinets")
    for obj in upCabinetsObjects:
        App.ActiveDocument.getObject("UpCabinets").addObject(App.ActiveDocument.getObject(obj+"_Fusion"))


def createPlots():
    #create plots
    name = "Plots"
    plotObjects = []

    #create spreadsheet column names
    App.activeDocument().addObject('Spreadsheet::Sheet', name + "_Spreadsheet")
    plotObjects.append(name + "_Spreadsheet")
    spreadSheetHeaders = ['Name', 'Width', 'Height', 'BoardThickness', 'WCantFront', 'WCantBack', 'HCantLeft', 'HCantRight', 'ByFlader']
    writeRecordInSpreadsheet(name + "_Spreadsheet", spreadSheetHeaders)

    plotProperties = []
    plotProperties.append(["_Right", 2180.0, App.Placement(App.Vector(-2252,-420,890), App.Rotation(0,0,0), App.Vector(0,0,0))])
    plotProperties.append(["_Front", 1570.0, App.Placement(App.Vector(-3642,-1356,890),App.Rotation(App.Vector(0,0,1),90))])
    plotProperties.append(["_Front1", 450.0, App.Placement(App.Vector(-3642,-346,890),App.Rotation(App.Vector(0,0,1),90))])
    plotProperties.append(["_Left", 2080.0, App.Placement(App.Vector(-2302,-2023,890), App.Rotation(0,0,0), App.Vector(0,0,0))])

    for plotProp in plotProperties:
        createPlot(name, plotProp[0], plotProp[1], plotObjects)
        App.activeDocument().getObject(name+plotProp[0]).Placement=plotProp[2]
    App.ActiveDocument.recompute()

    App.ActiveDocument.addObject("App::DocumentObjectGroup","Plots")
    for obj in plotObjects:
        App.ActiveDocument.getObject("Plots").addObject(App.ActiveDocument.getObject(obj))

def createBackForPlots():
    #create backs for plots
    name = "PlotsBacks"
    plotObjects = []

    #create spreadsheet column names
    App.activeDocument().addObject('Spreadsheet::Sheet', name + "_Spreadsheet")
    plotObjects.append(name + "_Spreadsheet")
    spreadSheetHeaders = ['Name', 'Width', 'Height', 'BoardThickness', 'WCantFront', 'WCantBack', 'HCantLeft', 'HCantRight', 'ByFlader']
    writeRecordInSpreadsheet(name + "_Spreadsheet", spreadSheetHeaders)

    plotProperties = []
    plotProperties.append(["_Right", 2100.0, 600.0, App.Placement(App.Vector(-2213,-115,1230),App.Rotation(App.Vector(1,0,0),90))])
#    plotProperties.append(["_Front", 1570.0, App.Placement(App.Vector(-3642,-1356,890),App.Rotation(App.Vector(0,0,1),90))])
#    plotProperties.append(["_Front1", 450.0, App.Placement(App.Vector(-3642,-346,890),App.Rotation(App.Vector(0,0,1),90))])
#    plotProperties.append(["_Left", 2080.0, App.Placement(App.Vector(-2302,-2023,890), App.Rotation(0,0,0), App.Vector(0,0,0))])

    for plotProp in plotProperties:
        createPlotBack(name, plotProp[0], plotProp[1], plotProp[2], plotObjects, 0.8, 18)
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

#createBaseCorpuses(890.0)
#createPlots()
#createVitodens()
#createBackForPlots()
createUpCorpuses(900)

#execfile('/home/nm/Dev/FreeCadScripts/createBaseCorpus.py')
