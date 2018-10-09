boardThickness = 18.0
cardboardThickness = 3.0
sCantT = 0.8
lCantT = 2.0
plotsBackMaterial = 'DecoriniQuads'
cabMaterial = 'WallnutTropic'
columnMaterial = 'ColumnMaterial'
baseLegHeight = 100.0
spaceBetweenDoors = 3.0
drawerSliderHole = 10.0
drawerSliderHoleToBottom = 12.0
colorsMap = {cabMaterial :       (1.0, 0.0, 0.0), 
             plotsBackMaterial : (0.0, 1.0, 0.0), 
             columnMaterial :    (0.0, 0.0, 1.0)}

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

def placeObjects(placementMatrix, namePrefix = ""):
    for p in placementMatrix:
         if ('xR' in p) and ('yR' in p) and ('zR' in p) and ('R' in p):
             App.ActiveDocument.getObject(namePrefix + p['name']).Placement = App.Placement(App.Vector(p['x'],p['y'],p['z']),App.Rotation(App.Vector(p['xR'],p['yR'],p['zR']),p['R']))
         elif 'vec' in p:
             vec = p['vec']
             App.ActiveDocument.getObject(namePrefix + p['name']).Placement = App.Placement(App.Vector(vec[0],vec[1],vec[2]),App.Rotation(vec[3],vec[4],vec[5]), App.Vector(0, 0, 0))


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

def createCircleInSketch(sketchName, radius, distX=None, distY=None):
    App.activeDocument().getObject(sketchName).addGeometry(Part.Circle(App.Vector(0,0,0),App.Vector(0,0,1),radius),False)
    if distX == None and distY == None:
        App.activeDocument().getObject(sketchName).addConstraint(Sketcher.Constraint('Coincident',0,3,-1,1))
    else:
        App.activeDocument().getObject(sketchName).addConstraint(Sketcher.Constraint('DistanceX',-2,1,0,3,distX))
        App.activeDocument().getObject(sketchName).addConstraint(Sketcher.Constraint('DistanceY',-1,1,0,3,distY))

def createLeg(cabinetName, bodyName, radius, legHeight, objects):
    createBody(bodyName, objects)
    sketchName = bodyName+"_Sketch"
    createSketch(sketchName, bodyName, 'XY_Plane', '')
    createCircleInSketch(sketchName, radius)
    createPadFromSketch(bodyName, sketchName, legHeight)

def createLegs(cabinetName, width, depth, objects):
    # create legs
    signW = -1
    signH = 1
    for legNum in range(1,5):
        bodyName = cabinetName + "_Leg" + str(legNum)
        createLeg(cabinetName, bodyName, 20, baseLegHeight, objects)
        signW = signW * (-1 if legNum%2==1 else 1)
        signH = signH * (1 if legNum%2==1 else -1)
        legWidth = (width/3)*signW
        legDepth = (depth/3)*signH
        App.activeDocument().getObject(bodyName).Placement=App.Placement(App.Vector(legWidth,legDepth,0), App.Rotation(0,0,180), App.Vector(0,0,0))
        App.ActiveDocument.recompute()

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

def createPocketFromSketch(bodyName, sketchName, zL):
    pocketName = sketchName + "_Pocket"
    App.activeDocument().getObject(bodyName).newObject("PartDesign::Pocket", pocketName)
    App.activeDocument().getObject(pocketName).Profile = App.activeDocument().getObject(sketchName)
    App.activeDocument().getObject(pocketName).Length = zL
    App.ActiveDocument.recompute()

def createBoardFromSheetRow(objName, bodyName, row):

    rowDict = getRowFromSpreadsheet(objName + "_Spreadsheet", row)
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

    holesCount = rowDict['Holes'] if 'Holes' in rowDict else 0
    holesSide = rowDict['HolesSide'] if 'HolesSide' in rowDict else '-'
    print str(holesCount) + "-" + str(holesSide)

    startDistX = -xL/2 + 30.0
    startDistY = -yL/2 + 30.0
    print str(startDistX) + "-" + str(startDistY)
    stepDist = max(xL,yL)/holesCount if holesSide == 'L' else min(xL, yL)/2
    for holeC in range(0, int(holesCount)):
        holeSketchName = sketchName + "_Hole" + str(holeC)
        createSketch(holeSketchName, bodyName, sketchName + "_Pad", 'Face5')
        distX = 0
        distY = 0
        if (holesSide == 'L' and yL>xL) or (holesSide == 'S' and yl<xL):
            distX = startDistX 
            distY = startDistY + holeC*stepDist
        elif (holesSide == 'L' and yL<xL) or (holesSide == 'S' and yL>xL):
            distX = startDistX + holeC*stepDist
            distY = startDistY
        createCircleInSketch(holeSketchName, 18.0, distX, distY)
        createPocketFromSketch(bodyName, holeSketchName, 15.0)
        App.ActiveDocument.recompute()

def createBoard(material, objName, boardName, width, height, objBoards, cants, boardThickness, fladder, holesCount=0, holesSide='-'):
    bodyName = objName + boardName
    createBody(bodyName, objBoards)
    calcWidth = width - cants[2] - cants[3]
    calcHeight = height - cants[0] - cants[1]
    sprRec = [bodyName + '_Sketch', int(round(calcWidth)), int(round(calcHeight)), boardThickness, cants[0], cants[1], cants[2], cants[3], fladder, material, holesCount, holesSide]
    row = writeRecordInSpreadsheet(objName + "_Spreadsheet", sprRec)
    createBoardFromSheetRow(objName, bodyName, row)

def createBoards(name, boardsList, placementMatrix, groupByName=False):
    plotObjects = []
    #create spreadsheet column names
    App.activeDocument().addObject('Spreadsheet::Sheet', name + "_Spreadsheet")
    plotObjects.append(name + "_Spreadsheet")
    spreadSheetHeaders = ['Name', 'Width', 'Height', 'BoardThickness', 'WCantFront', 'WCantBack', 'HCantLeft', 'HCantRight', 'ByFlader', 'Material', 'Holes', 'HolesSide']
    writeRecordInSpreadsheet(name + "_Spreadsheet", spreadSheetHeaders)

    for plotProp in boardsList:
        thickness = 18 if len(plotProp) <= 6 else plotProp[6]
        holesCount = 0 if len(plotProp) <= 7 else plotProp[7] 
        holesSide =  '-' if len(plotProp) <= 8 else plotProp[8]
        createBoard(plotProp[4],name, plotProp[0], plotProp[1], plotProp[2], plotObjects, plotProp[3], thickness, plotProp[5], holesCount, holesSide)

    placeObjects(placementMatrix, name)

    App.ActiveDocument.recompute()

    if groupByName:
        App.ActiveDocument.addObject("App::DocumentObjectGroup",name)
        for obj in plotObjects:
            App.ActiveDocument.getObject(name).addObject(App.ActiveDocument.getObject(obj))

def createFusion(itemName, objectsList):
    objectsFreeCad = []
    for objName in objectsList:
        objectsFreeCad.append(App.activeDocument().getObject(objName))

    App.activeDocument().addObject("Part::MultiFuse", itemName + "_Fusion")
    App.activeDocument().getObject(itemName + "_Fusion").Shapes = objectsFreeCad
    App.ActiveDocument.recompute()
            
def createCabinet(name, width, height, depth, addOns, visibleBack = False, isBase = True, isHavingBack = True, shiftBlend = 0.0, groupName = "", material=cabMaterial, doorsMaterial=cabMaterial, haveWholeBlend=False):

    objects = []

    pp = []
    placementMatrix = []
    
    #create base
    cants = [sCantT, sCantT if visibleBack else 0, sCantT, sCantT]
    baseCants = cants
    baseWidth = calcWidth = width;
    baseHeight = calcHeight = depth-(0 if visibleBack else cardboardThickness)
    pp.append(["_Base", calcWidth, calcHeight, cants, material, "W"])
    placementMatrix.append({'name':'_Base', 'vec' : (0, 0, 0, 0, 0, 0)})

    #create left side
    cants = [0, 0 if isBase else sCantT, sCantT, sCantT if visibleBack else 0]
    calcWidth = depth-(0 if visibleBack else cardboardThickness)
    calcHeight = height-boardThickness-(baseLegHeight if isBase else 0)
    pp.append(["_LeftSide", calcWidth, calcHeight, cants, material, "H"])
    placementMatrix.append({'name':'_LeftSide', 'vec' : (-width/2, 0, calcHeight/2+boardThickness, 90, 0, 90)})

    #create right side
    cants = [0 if isBase else sCantT, 0, sCantT, sCantT if visibleBack else 0]
    calcWidth = depth-(0 if visibleBack else cardboardThickness)
    calcHeight = height-boardThickness-(baseLegHeight if isBase else 0)
    pp.append(["_RightSide", calcWidth, calcHeight, cants, material, "H"])
    placementMatrix.append({'name':'_RightSide', 'vec' : (width/2, 0, calcHeight/2+boardThickness, 90, 0, -90)})
 
    if isBase and not haveWholeBlend:
        #create front blend
        cants = [sCantT, 0, 0, 0]
        calcWidth = width-2*boardThickness;
        calcHeight = 100
        pp.append(["_FrontBlend", calcWidth, calcHeight, cants, material, "-"])
        placementMatrix.append({'name':'_FrontBlend', 'vec' : (0, -baseHeight/2+calcHeight/2, height-baseLegHeight-boardThickness, 0, 0, 0)})

        #create back blend
        cants = [0, sCantT if visibleBack else 0, 0, 0]
        calcWidth = width-2*boardThickness;
        calcHeight = 100
        pp.append(["_BackBlend", calcWidth, calcHeight, cants, material, "-"])
        placementMatrix.append({'name':'_BackBlend', 'vec' : (0, baseHeight/2-calcHeight/2, height-baseLegHeight-boardThickness, 0, 0, 0)})

    else:
        #create whole blend
        cants = [sCantT, sCantT if visibleBack else 0, 0, 0]
        calcWidth = width-2*boardThickness;
        calcHeight = baseHeight
        pp.append(["_WholeBlend", calcWidth, calcHeight, cants, material, "W"])
        placementMatrix.append({'name':'_WholeBlend', 'vec' : (0, 0, height-boardThickness-shiftBlend-(baseLegHeight if isBase else 0), 0, 0, 0)})

    if isHavingBack:  
        cants = [0, 0, 0, 0]

        if not visibleBack:
            #create back from cardboard
            calcWidth = width - 3;
            calcHeight = height-(baseLegHeight if isBase else 0)-3
            pp.append(["_Back", calcWidth, calcHeight, cants, material+"_card", "H", cardboardThickness])
            placementMatrix.append({'name':'_Back', 'vec' : (0, baseHeight/2+cardboardThickness, height/2-(baseLegHeight if isBase else 0)/2, 0, 0, 90)});

        else:
            #create back from normal board
            calcWidth = width-2*boardThickness;
            calcHeight = height-(baseLegHeight if isBase else 0)-2*boardThickness
            pp.append(["_Back", calcWidth, calcHeight, cants, material, "H"])
            placementMatrix.append({'name':'_Back', 'vec' : (0, baseHeight/2+baseCants[1], height/2-(baseLegHeight if isBase else 0)/2, 0, 0, 90)})

    if 'list' not in addOns:
        addOns['list'] = []

    if 'doors' in addOns:
        doorsCount = addOns['doors']
        calcWidth = width/doorsCount - spaceBetweenDoors - (spaceBetweenDoors/(2*doorsCount) if 'doorsWallRight' in addOns else 0) - (spaceBetweenDoors/(2*doorsCount) if 'doorsWallLeft' in addOns else 0)
        calcHeight = height-(baseLegHeight+spaceBetweenDoors/2 if isBase else 0)-spaceBetweenDoors
        for curDoor in range(0, doorsCount):
            xPos = calcWidth*curDoor + calcWidth/2 - width/2 + spaceBetweenDoors/2
            if curDoor == 0 and 'doorsWallLeft' in addOns: xPos = xPos + spaceBetweenDoors/2
            if curDoor != 0: xPos = xPos + spaceBetweenDoors
            doorsHoles = addOns['doorsHoles'] if 'doorsHoles' in addOns else 0
            doorsHolesSide = addOns['doorsHolesSide'] if 'doorsHolesSide' in addOns else '-'
            addOns['list'].append(["_Door" + str(curDoor+1), calcWidth, calcHeight, [lCantT, lCantT, lCantT, lCantT], xPos, 0, 0, True, doorsHoles, doorsHolesSide])

    if 'shelves' in addOns:
        shelvesCount = addOns['shelves']
        calcWidth = width - 2*boardThickness
        calcHeight = depth - (boardThickness if visibleBack else cardboardThickness) - sCantT
        for curShelf in range(1, shelvesCount+1):
            yPos = (sCantT - boardThickness/2) if visibleBack else sCantT/2
            xPos = ((height-(baseLegHeight if isBase else 0))/(shelvesCount+1))*curShelf
            addOns['list'].append(["_Shelf" + str(curShelf), calcWidth, calcHeight, [sCantT, 0, 0, 0], 0, yPos, xPos, False])

    #create addOns
    for addOn in addOns['list']:
        doorsHoles = addOn[8] if len(addOn) >= 9 else 0
        doorsHolesSide = addOn[9] if len(addOn) >= 10 else '-'
        pp.append([addOn[0], addOn[1], addOn[2], addOn[3], doorsMaterial if addOn[7] else material, 'H' if addOn[7] else 'W', boardThickness, doorsHoles, doorsHolesSide])
        placementMatrix.append({'name':addOn[0], 'vec' : (addOn[4],(-baseHeight/2-baseCants[0]-2) if addOn[7] else addOn[5], ((height/2 - (baseLegHeight+spaceBetweenDoors/2 if isBase else 0)/2) if addOn[7] else 0) + addOn[6], 0, 0, (90 if addOn[7] else 0))});

    createBoards(name, pp, placementMatrix)
    objects.append(name + "_Spreadsheet")
    for ppItem in pp:
        objects.append(name + ppItem[0])

    #create drawers
    if 'drawers' in addOns:
        drawersCount = addOns['drawers']
        drawerHeight = (height - (baseLegHeight if isBase else 0) - spaceBetweenDoors/2)/drawersCount
        for curDrawer in range(1, drawersCount+1):
            createDrawer(name + "_Drawer" + str(curDrawer), width, drawerHeight, depth, visibleBack, material, doorsMaterial)
            objects.append(name + "_Drawer" + str(curDrawer) + "_Fusion")
            yA = -14 if visibleBack else -5.3;
            zA = spaceBetweenDoors/2+(curDrawer-1)*drawerHeight
            App.activeDocument().getObject(name + "_Drawer" + str(curDrawer) + "_Fusion").Placement=App.Placement(App.Vector(0,yA,zA), App.Rotation(0,0,0), App.Vector(0,0,0)) 

    if isBase:
        createLegs(name, width, depth, objects)

    createFusion(name, objects)

    if groupName != "":
        App.ActiveDocument.getObject(groupName).addObject(App.ActiveDocument.getObject(name+"_Fusion"))

def createDrawerSlider(name, sliderName, width, depth, isLeft):

    sliderDepth = (int(depth/50.0))*50.0
 
    #create spreadsheet column names
    App.activeDocument().addObject('Spreadsheet::Sheet', name + sliderName + "_Spreadsheet")
    spreadSheetHeaders = ['Name', 'Width', 'Height', 'BoardThickness', 'WCantFront', 'WCantBack', 'HCantLeft', 'HCantRight', 'ByFlader']
    writeRecordInSpreadsheet(name + sliderName + "_Spreadsheet", spreadSheetHeaders)

    bodyName = name + sliderName + "Body"
    createBody(bodyName, [])
    cants = [0, 0, 0, 0]
    calcWidth = 42.0
    calcHeight = sliderDepth
    sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, 42.0, cants[0], cants[1], cants[2], cants[3], 0]
    row = writeRecordInSpreadsheet(name + sliderName + "_Spreadsheet", sprRec)
    createBoardFromSheetRow(name + sliderName, name + sliderName + "Body", row)

    createSketch(bodyName + "_Pad1_Sketch", bodyName, bodyName + "_Sketch_Pad", "Face6")
    conList = []
    conList.append(Sketcher.Constraint('Distance',-1,1,0,250.0))
    conList.append(Sketcher.Constraint('Distance',-1,1,3,19.0) if isLeft else Sketcher.Constraint('Distance',-1,1,1,19.0))
    createRectInSketch(bodyName + "_Pad1_Sketch", 21, sliderDepth, conList)
    createPocketFromSketch(bodyName, bodyName + "_Pad1_Sketch", 32.0)
    Gui.activeDocument().hide(bodyName + "Pad1_Sketch")
    Gui.activeDocument().hide(bodyName + "_Sketch_Pad")

    createSketch(bodyName + "_Pad2_Sketch", bodyName, bodyName + "_Pad1_Sketch_Pocket", "Face4")
    conList = []
    conList.append(Sketcher.Constraint('Distance',-1,1,0,250.0))
    conList.append(Sketcher.Constraint('Distance',-1,1,1,21.0) if isLeft else Sketcher.Constraint('Distance',-1,1,3,21.0))
    createRectInSketch(bodyName + "_Pad2_Sketch", 19, sliderDepth, conList)
    createPocketFromSketch(bodyName, bodyName + "_Pad2_Sketch", 20.0)
    Gui.activeDocument().hide(bodyName + "_Pad2_Sketch")
    Gui.activeDocument().hide(bodyName + "_Pad1_Sketch")
    Gui.activeDocument().hide(bodyName + "_Pad1_Sketch_Pocket")

    App.activeDocument().getObject(name + sliderName + "Body").Placement = App.Placement(App.Vector((-1 if isLeft else 1)*(width-2*boardThickness-42)/2,0,21), App.Rotation(0,0,0), App.Vector(0,0,0))
    App.activeDocument().removeObject(name + sliderName + "_Spreadsheet")
    App.activeDocument().recompute()


def createDrawer(name, width, height, depth, visibleBack, material, doorsMaterial):

#    createDrawerSlider(name, "LeftSlider", width, (depth-sCantT-(boardThickness if visibleBack else cardboardThickness)-5), True);
#    createDrawerSlider(name, "RightSlider", width, (depth-sCantT-(boardThickness if visibleBack else cardboardThickness)-5), False);
#    objects = [name + "LeftSliderBody", name + "RightSliderBody"]
    objects = []

    pp = []
    placementMatrix = []

    #create door
    cants = [lCantT, lCantT, lCantT, lCantT]
    calcWidth = width-3;
    calcHeight = height-3
    zeroZ = (calcHeight+cants[0]+cants[1])/2
    pp.append(["_Door", calcWidth, calcHeight, cants, doorsMaterial, "H"])
    placementMatrix.append({'name':'_Door', 'vec' : (0,-(depth-sCantT-(boardThickness if visibleBack else cardboardThickness)-5)/2, zeroZ, 0, 0, 90)})

    #create front
    cants = [0, sCantT, 0, 0]
    calcWidth = width-4*boardThickness-10;
    calcHeight = height-2*30 - drawerSliderHole - cardboardThickness
    zeroZ = (calcHeight+cants[0]+cants[1])/2
    pp.append(["_Front", calcWidth, calcHeight, cants, material, "-"])
    placementMatrix.append({'name':'_Front', 'vec' : (0,-(depth-sCantT-3*(boardThickness if visibleBack else cardboardThickness)-5)/2, zeroZ+drawerSliderHole+2*cardboardThickness+drawerSliderHoleToBottom+boardThickness, 0, 0, 90)})

    #create left side
    cants = [sCantT, sCantT, 0, 0]
    calcWidth = depth-(boardThickness if visibleBack else cardboardThickness)-5
    calcHeight = height-2*30
    zeroZ = (calcHeight+cants[0]+cants[1])/2
    pp.append(["_LeftSide", calcWidth, calcHeight, cants, material, "-"])
    placementMatrix.append({'name':'_LeftSide', 'vec' : (-width/2+boardThickness+5,0,zeroZ+drawerSliderHoleToBottom+cardboardThickness+boardThickness, 90, 0, 90)})

    #create right side
    cants = [sCantT, sCantT, 0, 0]
    calcWidth = depth-(boardThickness if visibleBack else cardboardThickness)-5
    calcHeight = height-2*30
    zeroZ = (calcHeight+cants[0]+cants[1])/2
    pp.append(["_RightSide", calcWidth, calcHeight, cants, material, "-"])
    placementMatrix.append({'name':'_RightSide', 'vec' : (width/2-boardThickness-5,0,zeroZ+drawerSliderHoleToBottom+cardboardThickness+boardThickness, 90, 0, -90)})

    #create back
    cants = [0, sCantT, 0, 0]
    calcWidth = width-4*boardThickness-10
    calcHeight = height-2*30 - drawerSliderHole - cardboardThickness
    zeroZ = (calcHeight+cants[0]+cants[1])/2
    pp.append(["_Back", calcWidth, calcHeight, cants, material, "-"])
    placementMatrix.append({'name':'_Back', 'vec' : (0,(depth+sCantT-(boardThickness if visibleBack else cardboardThickness)-5)/2, zeroZ+drawerSliderHole+2*cardboardThickness+drawerSliderHoleToBottom+boardThickness, 0, 0, 90)})

    #create base
    cants = [0, 0, 0, 0]
    calcWidth = width-4*boardThickness+6;
    calcHeight = depth-(boardThickness if visibleBack else cardboardThickness)-5
    zeroZ = 0
    pp.append(["_Base", calcWidth, calcHeight, cants, material, "H"])
    placementMatrix.append({'name':'_Base', 'vec' : (0,0,zeroZ+drawerSliderHole+drawerSliderHoleToBottom+cardboardThickness+boardThickness, 0, 0, 0)})

    createBoards(name, pp, placementMatrix)
    objects.append(name + "_Spreadsheet")
    for ppItem in pp:
        objects.append(name + ppItem[0])

    createFusion(name, objects)

def createPlot(material, name, plotName, width, plotObjects):
    bodyName = name + plotName
    createBody(bodyName, plotObjects)
    cants = [0, 0, 0, 0]
    calcWidth = width
    calcHeight = 600
    sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, 40, cants[0], cants[1], cants[2], cants[3], 'W', material]
    row = writeRecordInSpreadsheet(name + "_Spreadsheet", sprRec)
    createBoardFromSheetRow(name, bodyName, row)

    App.activeDocument().getObject(name + plotName).newObject("PartDesign::Fillet",name + plotName + "Fillet")
    App.activeDocument().getObject(name + plotName + "Fillet").Base = (App.ActiveDocument.getObject(name + plotName + "_Sketch_Pad"),["Face3"])
    App.activeDocument().getObject(name + plotName + "Fillet").Radius = 6.0
    Gui.activeDocument().hide(name + plotName + "_Sketch")
    Gui.activeDocument().hide(name + plotName + "_Sketch_Pad")
    App.activeDocument().recompute()

def createBaseCorpuses(height):
    #creating base corpuses

    App.ActiveDocument.addObject("App::DocumentObjectGroup","BaseCabinets")

    createCabinet('Bottles', 300.0, height, 560.0, {'doors': 1, 'doorsWallRight': True}, groupName="BaseCabinets")

    addOns = {'list' : [["Shelf1", 564.0, 526.2, [0.8, 0, 0, 0], 0, -15.40, 122.0, False], 
                        ["Door1", 597.0, 137.0, [2, 2, 2, 2], 0, 0, -309.5, True, 2, 'L']]}
    createCabinet('Oven', 600.0, height, 560.0, addOns, groupName="BaseCabinets")

    addOns = {'shelves' : 1, 'list' : [["Plank1", 100.0, height-103.0, [0,0,0,0], -557, 0, 0, True],
              ["Plank2", 197.0, height-103.0, [2,2,0,2], -90, 0, 0, True], 
              ["Door1", 597.0, height-103.0, [2,2,2,2], 310, 0, 0, True, 2, 'L']]}
    createCabinet('Cab1', 1220.0, height, 500.0, addOns, groupName="BaseCabinets")

    createCabinet('Cab2', 442.0, height, 510.0, {'doors' : 1, 'doorsWallRight' : True, 'shelves': 1, 'doorsHoles' : 2, 'doorsHolesSide': 'L'}, groupName="BaseCabinets")
    createCabinet('Sink', 600.0, height, 560.0, {'doors' : 1, 'doorsWallLeft' : True, 'doorsHoles' : 2, 'doorsHolesSide': 'L'}, groupName="BaseCabinets")

    addOns = {'shelves' : 1, 'list':[["Plank1", 100.0, height-103.0, [0,0,0,0], 492, 0, 0, True],
              ["Plank2", 197.0, height-103.0, [2,2,2,0], 7.5, 0, 0, True], 
              ["Door1", 450.0, height-103.0, [2,2,2,2], -318.5, 0, 0, True, 2, 'L']]}
    createCabinet('Cab3', 1090.0, height, 370.0, addOns, groupName="BaseCabinets")
 
    createCabinet('Cab4', 600.0, height, 560.0, {'drawers' : 4}, visibleBack=True, groupName="BaseCabinets")
    createCabinet('Cab5', 968.0, height, 560.0, {'shelves' : 1, 'doors' : 2, 'doorsHoles' : 2, 'doorsHolesSide': 'L'}, visibleBack=True, groupName="BaseCabinets")

    placementMatrix = [{'name':'Bottles_Fusion','x':-1316, 	'y':-402,	'z':100,	'xR':0,	'yR':0, 'zR':1, 'R':0},
                       {'name':'Oven_Fusion',	'x':-1766, 	'y':-402, 	'z':100,	'xR':0,	'yR':0, 'zR':1, 'R':0},
                       {'name':'Cab1_Fusion',	'x':-3276, 	'y':-432, 	'z':100,	'xR':0,	'yR':0, 'zR':1, 'R':0},
                       {'name':'Cab2_Fusion',	'x':-3630, 	'y':-922, 	'z':100,	'xR':0, 'yR':0, 'zR':1, 'R':90},
                       {'name':'Sink_Fusion',	'x':-3655, 	'y':-1443, 	'z':100,	'xR':0, 'yR':0, 'zR':1, 'R':90},
                       {'name':'Cab3_Fusion',	'x':-3391, 	'y':-1947, 	'z':100,	'xR':0, 'yR':0, 'zR':1, 'R':180},
                       {'name':'Cab4_Fusion',	'x':-2546, 	'y':-2043, 	'z':100,	'xR':0, 'yR':0, 'zR':1, 'R':180},
                       {'name':'Cab5_Fusion',	'x':-1762, 	'y':-2043, 	'z':100,	'xR':0, 'yR':0, 'zR':1, 'R':180}]

    placeObjects(placementMatrix)

def createUpCorpuses(height, depth):
    #creating up corpuses

    App.ActiveDocument.addObject("App::DocumentObjectGroup","UpCabinets")

    createCabinet('BottlesUp', 300.0, height-253.0, depth, {'shelves':1, 'doors' : 1, 'doorsWallLeft' : True}, isBase=False, groupName='UpCabinets')

    addOns = {'shelves':1, 'list': [["Door1", 597.0, height-40-3, [2, 2, 2, 2], 0, 0, 0, True]] }
    createCabinet('OvenUp', 600.0, height-40, depth, addOns, isBase=False, shiftBlend=220.0, groupName='UpCabinets')

    createCabinet('Cab1Up', 1160.0, height, depth, {'shelves' : 2, 'doors' : 2, 'doorsWallRight' : True}, isBase=False, groupName='UpCabinets')
    createCabinet('Cab2Up', 700.0, height+150, 480.0, {'doors' : 1, 'doorsWallRight' : True}, isBase=False, isHavingBack=False, groupName='UpCabinets')
    createCabinet('Cab3Up', 600.0, height, 253.0, {'shelves' : 2, 'doors' : 1}, isBase=False, groupName='UpCabinets')

    placementMatrix = [{'name':'BottlesUp_Fusion',	'x':-1316,      'y':-266,       'z':2197,        'xR':0, 'yR':1, 'zR':0, 'R':180},
                       {'name':'OvenUp_Fusion',		'x':-1766,      'y':-266,       'z':2450,        'xR':0, 'yR':1, 'zR':0, 'R':180},
                       {'name':'Cab1Up_Fusion',         'x':-2646,      'y':-266,       'z':2450,        'xR':0, 'yR':1, 'zR':0, 'R':180},
                       {'name':'Cab2Up_Fusion',         'x':-3577,      'y':-371,       'z':2450,        'xR':0, 'yR':1, 'zR':0, 'R':180},
                       {'name':'Cab3Up_Fusion',         'x':-3160,      'y':-2019,      'z':1500,        'xR':0, 'yR':0, 'zR':1, 'R':180}]

    placeObjects(placementMatrix)

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
    plotProperties.append(["_Right", 2172.0, App.Placement(App.Vector(-2252,-420,height-40),  App.Rotation(App.Vector(0,0,1),0))])
    plotProperties.append(["_Front", 2020.0, App.Placement(App.Vector(-3640,-1130,height-40), App.Rotation(App.Vector(0,0,1),90))])
    plotProperties.append(["_Left", 2060.0, App.Placement(App.Vector(-2308,-2023,height-40),  App.Rotation(App.Vector(0,0,1),180))])

    for plotProp in plotProperties:
        createPlot('PlotsGranite', name, plotProp[0], plotProp[1], plotObjects)
        App.activeDocument().getObject(name+plotProp[0]).Placement=plotProp[2]
    App.ActiveDocument.recompute()

    createSketch("Plots_Front_Sink_Sketch", "Plots_Front", "Plots_Front_Sketch_Pad", "Face6")
    conList = []
    conList.append(Sketcher.Constraint('Distance',-1,1,3,580.0))
    conList.append(Sketcher.Constraint('Distance',-1,1,2,240.0))
    createRectInSketch("Plots_Front_Sink_Sketch", 980, 480, conList)
    createPocketFromSketch("Plots_Front", "Plots_Front_Sink_Sketch", 40.0)
    Gui.activeDocument().hide("Plots_Front_Sketch_Pad")

    createSketch("Plots_Right_Bosch_Sketch", "Plots_Right", "Plots_Right_Sketch_Pad", "Face6")
    conList = []
    conList.append(Sketcher.Constraint('Distance',-1,1,1,766.0))
    conList.append(Sketcher.Constraint('Distance',-1,1,0,250.0))
    createRectInSketch("Plots_Right_Bosch_Sketch", 560, 490, conList)
    createPocketFromSketch("Plots_Right", "Plots_Right_Bosch_Sketch", 40.0)
    Gui.activeDocument().hide("Plots_Right_Sketch_Pad")

    App.ActiveDocument.addObject("App::DocumentObjectGroup","Plots")
    for obj in plotObjects:
        App.ActiveDocument.getObject("Plots").addObject(App.ActiveDocument.getObject(obj))

def createBackForPlots(height):
    #create backs for plots

    s = sCantT

    pp = []
    pp.append(["_Right1", 2100.0, height,    [0, 0, 0, 0], plotsBackMaterial, "W"])
    pp.append(["_Front1", 70.0,   height,    [0, s, 0, 0], plotsBackMaterial, "W"])
    pp.append(["_Front2", 1320.0, 115.0,     [0, 0, 0, 0], plotsBackMaterial, "W"])
    pp.append(["_Front3", 620.0,  height,    [0, s, 0, 0], plotsBackMaterial, "W"])
    pp.append(["_Front4", 200.0,  465.0,     [0, s, s, 0], plotsBackMaterial, "W"])
    pp.append(["_Front5", 200.0,  465.0,     [0, s, s, 0], plotsBackMaterial, "W"])
    pp.append(["_Left1",  1072.0, height,    [s, 0, 0, 0], plotsBackMaterial, "W"])
    pp.append(["_Left2",  203.0,  height,    [0, 0, 0, s], plotsBackMaterial, "W"])
    pp.append(["_Left3",  1541.0, height,    [0, 0, 0, 0], plotsBackMaterial, "W"])
    pp.append(["_Left4",  203.0,  height,    [0, 0, 0, s], plotsBackMaterial, "W"])
    pp.append(["_Left5",  1577.0, 202.5,     [0, s, s, s], plotsBackMaterial, "W"])
    pp.append(["_Left2D", 167.0,  height-18, [0, 0, 0, s], plotsBackMaterial, "W"])
    pp.append(["_Left4D", 167.0,  height-18, [0, 0, 0, s], plotsBackMaterial, "W"])
    pp.append(["_Left5D", 1541.0, 166.0,     [0, s, 0, 0], plotsBackMaterial, "W"])


    placementMatrix = [{'name':'_Right1',      'vec' : (-2216,    -115,  1200,    0,  0, 90)},
                       {'name':'_Front1',      'vec' : (-3945,    -2110, 1200,    90, 0, 90)},
                       {'name':'_Front2',      'vec' : (-3945,    -1415, 957,     90, 0, 90)},
                       {'name':'_Front3',      'vec' : (-3945,    -445,  1200,    90, 0, 90)}, 
                       {'name':'_Front4',      'vec' : (-4027,    -2057, 1267,    0,  0, 90)},
                       {'name':'_Front5',      'vec' : (-4027,    -755,  1267,    0,  0, 90)},
                       {'name':'_Left1',       'vec' : (-3391,    -2127, 1200,    0,  0, 90)},
                       {'name':'_Left2',       'vec' : (-2855,    -2229, 1200,    90, 0, 90)},
                       {'name':'_Left3',       'vec' : (-2066.5,  -2294, 1200,    0,  0, 90)},
                       {'name':'_Left4',       'vec' : (-1296,    -2229, 1200,    90, 0, 90)},
                       {'name':'_Left5',       'vec' : (-2066.5,  -2228.5, 1500,    0,  0, 0 )},
                       {'name':'_Left2D',      'vec' : (-2837,    -2211, 1191,    90, 0, 90)},
                       {'name':'_Left4D',      'vec' : (-1314,    -2211, 1191,    90, 0, 90)},
                       {'name':'_Left5D',      'vec' : (-2066.5,  -2210.5, 1482,    0,  0, 0 )}]

    createBoards("PlotsBacks", pp, placementMatrix, groupByName=True)

def createVitodensDownCabinet():
    pp = []
    pp.append(["_RightBoard",  200.0,  450.0,  [0.8, 0.8, 0.8, 0.8], cabMaterial, "H"])
    pp.append(["_DownPlank",   700.0,  100.0,  [0.8, 2, 0.8, 2],     cabMaterial, "H"])
    pp.append(["_Door",        695.5,  345.5,  [2, 2, 2, 2],         cabMaterial, "H"])
    pp.append(["_LeftBoard",   200.0,  450.0,  [0.8, 0.8, 0.8, 0.8], cabMaterial, "H"])

    placementMatrix = [{'name':'_RightBoard', 'vec' : (-3245,    -233,  1125,    90, 0, 90)},
                       {'name':'_DownPlank', 'vec' : (-3577.6,  -333,  949.4,   0,  0, 90)},
                       {'name':'_Door', 'vec' : (-3576.25, -333,  1175.75, 0,  0, 90)},
                       {'name':'_LeftBoard', 'vec' : (-3927,    -233,  1125,    90, 0, 90)}]

    createBoards("VitodensDownCab", pp, placementMatrix)

def createKitchenDownPlanks():
    pp = []
    pp.append(["_Right1_Down", 2310.0, 100.0,  [0.8, 0.8, 0.8, 0.8], cabMaterial, "W"])
    pp.append(["_Front1_Down", 1173.0, 100.0,  [0.8, 0.8, 0.8, 0.8], cabMaterial, "W"])
    pp.append(["_Left1_Down",  2210.0, 100.0,  [0.8, 0.8, 0.8, 0.8], cabMaterial, "W"])
    pp.append(["_Left2_Down",  560.0,  100.0,  [0.8, 0.8, 0.8, 0.8], cabMaterial, "W"])

    placementMatrix = [{'name':"_Right1_Down", 'vec':  (-2321,    -617,  50,      0,  0, 90)},
                       {'name':"_Front1_Down", 'vec':  (-3430,    -1221, 50,      90, 0, 90)},
                       {'name':"_Left1_Down",  'vec':  (-2401,    -1808, 50,      0,  0, 90)},
                       {'name':"_Left2_Down",  'vec':  (-1296,    -2043, 50,      90, 0, 90)}]

    createBoards("KitchenDownPlanks", pp, placementMatrix)

def createColumnBoards():

    pp = []
    pp.append(["_Column1",     620.0,  2200.0, [0.8, 0.8, 0.8, 0.8], columnMaterial, "H"])
    pp.append(["_Column2",     694.0,  2450.0, [0.8, 0.8, 0.8, 0.8], columnMaterial, "H"])
    pp.append(["_Column3",     620.0,  2450.0, [0.8, 0.8, 0.8, 0.8], columnMaterial, "H"])

    placementMatrix = [{'name':"_Column1",     'vec':  (-1163,    -425,  1100,    90, 0, 90)},
                       {'name':"_Column2",     'vec':  (-816,     -735,  1225,    0,  0, 90)},
                       {'name':"_Column3",     'vec':  (-487,     -425,  1225,    90, 0, 90)}]

    createBoards("KitchenColumn", pp, placementMatrix)

def createAdditionalBoards():
    pp = []
    pp.append(["_VitoCabAdd1", 477.0,  950.0, [0.8,   0.8, 0.8, 0.8], cabMaterial, "-"])
    pp.append(["_WindowBack",  1541.0, 600.0, [0,     0,   0,   0],   cabMaterial, "H"])
    pp.append(["_DishDoor",    597.0,  757.0, [2,     2,   2,   2],   cabMaterial, "H"])
    pp.append(["_DishUp1",     600.0,  100.0, [0,     0,   0,   0],   cabMaterial, "-"])
    pp.append(["_DishUp2",     600.0,  100.0, [0,     0,   0,   0],   cabMaterial, "-"])
    pp.append(["_DishUp3",     600.0,  100.0, [0.8,   0,   0,   0], cabMaterial, "-"])
    pp.append(["_DishUp4",     600.0,  100.0, [0.8,   0,   0,   0], cabMaterial, "-"])

    placementMatrix = [{'name':"_VitoCabAdd1", 'vec':  (-3945,    -371.4, 1975, 90, 0, 90)},
                       {'name':'_WindowBack',  'vec' : (-2066.5,  -2312,  1200, 0, 0, 90)},
                       {'name':'_DishDoor',    'vec' : (-2366.0,  -683,   479,  0, 0, 90)},
                       {'name':'_DishUp1',     'vec' : (-2366.0,  -234,   824,  0, 0, 0)},
                       {'name':'_DishUp2',     'vec' : (-2366.0,  -234,   842,  0, 0, 0)},
                       {'name':'_DishUp3',     'vec' : (-2366.0,  -630,   824,  0, 0, 0)},
                       {'name':'_DishUp4',     'vec' : (-2366.0,  -630,   842,  0, 0, 0)}]
    
    createBoards("KitchenAddons", pp, placementMatrix)

def createShelvesAroundKitchenWindow():
    pp = []
    pp.append(["_ShelvesR1",    250.0,  950.0, [0.8,   0.8,   0.8,   0.8], cabMaterial, "H"])
    pp.append(["_ShelvesR2",    232.0,  950.0, [0.8,   0.8,   0.8,   0.8], cabMaterial, "H"])
    pp.append(["_ShelvesR3",    232.0,  232.0, [0,     0,     0,     0],   cabMaterial, "-"])
    pp.append(["_ShelvesR4",    232.0,  232.0, [0,     0,     0,     0],   cabMaterial, "-"])
    pp.append(["_ShelvesR5",    232.0,  232.0, [0,     0,     0,     0],   cabMaterial, "-"])

    pp.append(["_ShelvesL1",    436.0,  950.0, [0.8,   0.8,   0.8,   0.8], cabMaterial, "H"])
    pp.append(["_ShelvesL2",    250.0,  436.0, [0,     0,     0,     0],   cabMaterial, "-"])
    pp.append(["_ShelvesL3",    250.0,  436.0, [0,     0,     0,     0],   cabMaterial, "-"])
    pp.append(["_ShelvesL4",    250.0,  436.0, [0,     0,     0,     0],   cabMaterial, "-"])



    placementMatrix = [{'name':"_ShelvesR1", 'vec':  (-3478,    -2020.0, 1975, 90, 0, 90)}, 
                       {'name':"_ShelvesR2", 'vec':  (-3594,    -2127.0, 1975, 0, 0, 90)},
                       {'name':"_ShelvesR3", 'vec':  (-3594,    -2011.0, 1500, 0, 0, 0)},
                       {'name':"_ShelvesR4", 'vec':  (-3594,    -2011.0, 1900, 0, 0, 0)},
                       {'name':"_ShelvesR5", 'vec':  (-3594,    -2011.0, 2300, 0, 0, 0)},
                       {'name':"_ShelvesL1", 'vec':  (-2855,    -2112.0, 1975, 90, 0, 90)}, 
                       {'name':"_ShelvesL2", 'vec':  (-2711,    -2112.0, 1500, 0, 0, 0)},
                       {'name':"_ShelvesL3", 'vec':  (-2711,    -2112.0, 1900, 0, 0, 0)},
                       {'name':"_ShelvesL4", 'vec':  (-2711,    -2112.0, 2300, 0, 0, 0)}]

    createBoards("ShelvesKitchenWindow", pp, placementMatrix, groupByName=True)


def createLivingRoomShelves():
    
    pp = []
    pp.append(["_LivRoom1",    1500.0, 470.0,  [2, 0, 0, 0],         cabMaterial, "W"])
    pp.append(["_LivRoom2",    1500.0, 300.0,  [2, 0, 0, 0],         cabMaterial, "W"])
    pp.append(["_LivRoom3",    1500.0, 300.0,  [2, 0, 0, 0],         cabMaterial, "W"])

    placementMatrix = [{'name':"_LivRoom1",    'vec':  (2051,     -349,  900,     0,  0, 0)},
                       {'name':"_LivRoom2",    'vec':  (2051,     -264,  1100,    0,  0, 0)},
                       {'name':"_LivRoom3",    'vec':  (2051,     -264,  1500,    0,  0, 0)}]

    createBoards("LivingShelves", pp, placementMatrix)

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
    sprRec = [bodyName + '_Sketch', calcWidth, calcHeight, 1000.0, cants[0], cants[1], cants[2], cants[3], 0]
    row = writeRecordInSpreadsheet("Vitodens_Spreadsheet", sprRec)
    createBoardFromSheetRow("Vitodens", "Vitodens_111W", row)

    App.activeDocument().getObject("Vitodens_111W").Placement = App.Placement(App.Vector(-3585,-355,1400), App.Rotation(0,0,0), App.Vector(0,0,0))

    App.ActiveDocument.addObject("App::DocumentObjectGroup","Vitodens")
    App.ActiveDocument.getObject("Vitodens").addObject(App.ActiveDocument.getObject("Vitodens_Spreadsheet"))
    App.ActiveDocument.getObject("Vitodens").addObject(App.ActiveDocument.getObject("Vitodens_111W"))

def createLivingRoomCorpuses():
    #creating up corpuses

    App.ActiveDocument.addObject("App::DocumentObjectGroup","LivingCabinets")

    createCabinet('LivCab1', 500.0, 2200.0, 450.0, {'shelves':5, 'doors' : 1, 'doorsWallLeft' : True}, groupName='LivingCabinets', haveWholeBlend=True)
    createCabinet('LivCab2', 500.0, 1800.0, 450.0, {'shelves':4, 'doors' : 1}, groupName='LivingCabinets', haveWholeBlend=True)
    createCabinet('LivCab3', 500.0, 900.0, 450.0, {'drawers' : 4}, groupName='LivingCabinets')
    createCabinet('LivCab4', 500.0, 900.0, 450.0, {'drawers' : 2}, groupName='LivingCabinets')
    createCabinet('LivCab5', 500.0, 900.0, 450.0, {'drawers' : 4}, groupName='LivingCabinets')
    createCabinet('LivCab6', 500.0, 1800.0, 450.0, {'shelves':4, 'doors' : 1}, groupName='LivingCabinets', haveWholeBlend=True)
    createCabinet('LivCab7', 500.0, 2200.0, 450.0, {'shelves':5, 'doors' : 1}, groupName='LivingCabinets', haveWholeBlend=True)
    createCabinet('LivCab2_Up', 500.0, 400.0, 450.0, {'doors' : 2, 'shelves':1}, groupName='LivingCabinets', isBase=False)
    createCabinet('LivCab3_Up', 500.0, 400.0, 450.0, {'doors' : 2, 'shelves':1}, groupName='LivingCabinets', isBase=False)
    createCabinet('LivCab4_Up', 500.0, 400.0, 450.0, {'doors' : 2, 'shelves':1}, groupName='LivingCabinets', isBase=False)
    createCabinet('LivCab5_Up', 500.0, 400.0, 450.0, {'doors' : 2, 'shelves':1}, groupName='LivingCabinets', isBase=False)
    createCabinet('LivCab6_Up', 500.0, 400.0, 450.0, {'doors' : 2, 'shelves':1}, groupName='LivingCabinets', isBase=False)
    createCabinet('LivCab8', 300.0, 882.0, 300.0, {}, groupName='LivingCabinets', isBase=False, visibleBack=True)
    createCabinet('LivCab9', 770.0, 300.0, 300.0, {'doors' : 2, 'shelves':1, 'doorsWallLeft' : True}, groupName='LivingCabinets', isBase=False)

    placementMatrix = [{'name':'LivCab1_Fusion',      'x':551,       'y':-341,       'z':100,        'xR':0, 'yR':1, 'zR':0, 'R':0},
                       {'name':'LivCab2_Fusion',      'x':1051,      'y':-341,       'z':100,        'xR':0, 'yR':1, 'zR':0, 'R':0},
                       {'name':'LivCab3_Fusion',      'x':1551,      'y':-341,       'z':100,        'xR':0, 'yR':1, 'zR':0, 'R':0},
                       {'name':'LivCab4_Fusion',      'x':2051,      'y':-341,       'z':100,        'xR':0, 'yR':1, 'zR':0, 'R':0},
                       {'name':'LivCab5_Fusion',      'x':2551,      'y':-341,       'z':100,        'xR':0, 'yR':1, 'zR':0, 'R':0},
                       {'name':'LivCab6_Fusion',      'x':3051,      'y':-341,       'z':100,        'xR':0, 'yR':1, 'zR':0, 'R':0},
                       {'name':'LivCab7_Fusion',      'x':3551,      'y':-341,       'z':100,        'xR':0, 'yR':1, 'zR':0, 'R':0},
                       {'name':'LivCab2_Up_Fusion',   'x':1051,      'y':-341,       'z':1800,       'xR':0, 'yR':1, 'zR':0, 'R':0},
                       {'name':'LivCab3_Up_Fusion',   'x':1551,      'y':-341,       'z':1800,       'xR':0, 'yR':1, 'zR':0, 'R':0},
                       {'name':'LivCab4_Up_Fusion',   'x':2051,      'y':-341,       'z':1800,       'xR':0, 'yR':1, 'zR':0, 'R':0},
                       {'name':'LivCab5_Up_Fusion',   'x':2551,      'y':-341,       'z':1800,       'xR':0, 'yR':1, 'zR':0, 'R':0},
                       {'name':'LivCab6_Up_Fusion',   'x':3051,      'y':-341,       'z':1800,       'xR':0, 'yR':1, 'zR':0, 'R':0},
                       {'name':'LivCab8_Fusion',      'x':2051,      'y':-256,       'z':918,        'xR':0, 'yR':1, 'zR':0, 'R':0},
                       {'name':'LivCab9_Fusion',      'x':-84,       'y':-416,       'z':1900,       'xR':0, 'yR':1, 'zR':0, 'R':0}]

    placeObjects(placementMatrix)

def createSmallRoomCorpuses():
    App.ActiveDocument.addObject("App::DocumentObjectGroup","SmallRoomCabinets")

    createCabinet('SRCab1', 990.0, 700.0, 590.0, {'drawers':3, 'doorsWallLeft' : True, 'doorsWallRight' : True}, groupName='SmallRoomCabinets')
    createCabinet('SRCab2', 990.0, 1300.0, 590.0, {'doors':2, 'doorsWallLeft' : True, 'doorsWallRight' : True}, groupName='SmallRoomCabinets', isBase=False)
    createCabinet('SRCab3', 990.0, 530.0, 590.0, {'doors':2, 'shelves':1, 'doorsWallLeft' : True, 'doorsWallRight' : True}, groupName='SmallRoomCabinets', haveWholeBlend=True, isBase=False)

    placementMatrix = [{'name':'SRCab1_Fusion',      'x':-500,       'y':-311,       'z':100,        'xR':0, 'yR':1, 'zR':0, 'R':0},
                       {'name':'SRCab2_Fusion',      'x':-500,       'y':-311,       'z':700,        'xR':0, 'yR':1, 'zR':0, 'R':0},
                       {'name':'SRCab3_Fusion',      'x':-500,       'y':-311,       'z':2000,       'xR':0, 'yR':1, 'zR':0, 'R':0}]

    placeObjects(placementMatrix)

    pp = [["_Down1", 990.0, 100.0, [0.8, 0.8, 0.8, 0.8], cabMaterial, "H"]]
    placementMatrix = [{'name':"_Down1", 'vec':  (-500,-586,50, 90, 0, 90)}]
    createBoards("SR", pp, placementMatrix)

    App.ActiveDocument.getObject("SmallRoomCabinets").addObject(App.ActiveDocument.getObject("SR_Spreadsheet"))
    App.ActiveDocument.getObject("SmallRoomCabinets").addObject(App.ActiveDocument.getObject("SR_Down1"))


def createCorridorCorpuses():
    App.ActiveDocument.addObject("App::DocumentObjectGroup","CorridorCabinets")

    createCabinet('CorCab1', 915.0, 700.0, 500.0, {'drawers':3, 'doorsWallRight' : True}, groupName='CorridorCabinets')
    createCabinet('CorCab2', 915.0, 1300.0, 500.0, {'doors':2,  'doorsWallRight' : True}, groupName='CorridorCabinets', isBase=False)
    createCabinet('CorCab3', 915.0, 530.0, 500.0, {'doors':2, 'shelves':1, 'doorsWallRight' : True}, groupName='CorridorCabinets', haveWholeBlend=True, isBase=False)

    createCabinet('CorCab4', 915.0, 700.0, 500.0, {'drawers':3, 'doorsWallLeft' : True}, groupName='CorridorCabinets')
    createCabinet('CorCab5', 915.0, 1300.0, 500.0, {'doors':2, 'doorsWallLeft' : True}, groupName='CorridorCabinets', isBase=False)
    createCabinet('CorCab6', 915.0, 530.0, 500.0, {'doors':2, 'shelves':1, 'doorsWallLeft' : True}, groupName='CorridorCabinets', haveWholeBlend=True, isBase=False)


    placementMatrix = [{'name':'CorCab1_Fusion',      'x':-257,       'y':463,       'z':100,        'xR':0, 'yR':0, 'zR':1, 'R':270},
                       {'name':'CorCab2_Fusion',      'x':-257,       'y':463,       'z':700,        'xR':0, 'yR':0, 'zR':1, 'R':270},
                       {'name':'CorCab3_Fusion',      'x':-257,       'y':463,       'z':2000,       'xR':0, 'yR':0, 'zR':1, 'R':270},
                       {'name':'CorCab4_Fusion',      'x':-257,       'y':1378,       'z':100,        'xR':0, 'yR':0, 'zR':1, 'R':270},
                       {'name':'CorCab5_Fusion',      'x':-257,       'y':1378,       'z':700,        'xR':0, 'yR':0, 'zR':1, 'R':270},
                       {'name':'CorCab6_Fusion',      'x':-257,       'y':1378,       'z':2000,       'xR':0, 'yR':0, 'zR':1, 'R':270}]

    placeObjects(placementMatrix)

    pp = [["_Down1", 1830.0, 100.0, [0.8, 0.8, 0.8, 0.8], cabMaterial, "H"]]
    placementMatrix = [{'name':"_Down1", 'vec':  (-500, 921, 50, 90, 90, 90)}]
    createBoards("Cor", pp, placementMatrix)

    App.ActiveDocument.getObject("SmallRoomCabinets").addObject(App.ActiveDocument.getObject("Cor_Spreadsheet"))
    App.ActiveDocument.getObject("SmallRoomCabinets").addObject(App.ActiveDocument.getObject("Cor_Down1"))

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
        spreadSheetHeaders = ['Name', 'Length', 'Width', 'Count', 'CanRotate', 'LongCantCount', 'ShortCantCount', 'EdgeThickness', 'CantMaterial', 'PantsHolesCount', 'SideForHoles']
        writeRecordInSpreadsheet(mat + "_Spreadsheet", spreadSheetHeaders)

        for x in finalDict[mat]:
            length = x['Height'] if x['ByFlader']=='H' else (x['Width'] if x['ByFlader']=='W' else max(x['Height'], x['Width']))
            width = x['Width'] if x['ByFlader']=='H' else (x['Height'] if x['ByFlader']=='W' else min(x['Height'], x['Width']))
            longEdgeCount = int(x['WCantFront'] > 0) + int(x['WCantBack'] > 0) if x['Width'] > x['Height'] else int(x['HCantLeft'] > 0) + int(x['HCantRight'] > 0)
            shortEdgeCount = int(x['HCantLeft'] > 0) + int(x['HCantRight'] > 0) if x['Width'] > x['Height'] else int(x['WCantFront'] > 0) + int(x['WCantBack'] > 0)
            edgeThickness = max(x['WCantFront'], x['WCantBack'], x['HCantLeft'], x['HCantRight'])
            canRotate = 0 if x['ByFlader']=='H' else (0 if x['ByFlader']=='W' else 1)

            row = [x['Name'], length, width, x['Count'], canRotate, longEdgeCount, shortEdgeCount, edgeThickness, x['Material'], x['Holes'], x['HolesSide']]
            writeRecordInSpreadsheet(mat + "_Spreadsheet", row)
                    
######################################
# Kitchen and Living room
######################################
#createBaseCorpuses(860.0)
#createPlots(900)
#createVitodens()
#createBackForPlots(600.0)
#createVitodensDownCabinet()
#createKitchenDownPlanks()
#createColumnBoards()
#createAdditionalBoards()
createShelvesAroundKitchenWindow()
#createUpCorpuses(950.0, 300.0)
#createLivingRoomCorpuses()
#createLivingRoomShelves()

#######################################
# Small room
#######################################
#createSmallRoomCorpuses()

#######################################
# Corridor
#######################################
#createCorridorCorpuses()

#######################################
#Final Processing
#######################################
#processAllSpreadSheetsByMaterial()

#execfile('/home/nm/Dev/FreeCadScripts/createBaseCorpus.py')
