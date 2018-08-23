def createBody(bodyName):
    App.activeDocument().addObject('PartDesign::Body', bodyName)
    App.ActiveDocument.recompute()
    App.activeDocument().addObject('Spreadsheet::Sheet', bodyName+"_Spreadsheet")

def createSketch(sketchName, bodyName, supportName, supportFace):
    getattr(App.activeDocument(), bodyName).newObject('Sketcher::SketchObject', sketchName)
    getattr(App.activeDocument(), sketchName).Support = (getattr(App.activeDocument(), supportName), [supportFace])
    getattr(App.activeDocument(), sketchName).MapMode = 'FlatFace'
    App.ActiveDocument.recompute()

def createRectangle(width, height, depth, bodyName, sketchName, padName, extraConList):

    geoList = []
    geoList.append(Part.LineSegment(App.Vector(-1.396005,1.166614,0),App.Vector(2.077621,1.166614,0)))
    geoList.append(Part.LineSegment(App.Vector(2.077621,1.166614,0),App.Vector(2.077621,-1.468099,0)))
    geoList.append(Part.LineSegment(App.Vector(2.077621,-1.468099,0),App.Vector(-1.396005,-1.468099,0)))
    geoList.append(Part.LineSegment(App.Vector(-1.396005,-1.468099,0),App.Vector(-1.396005,1.166614,0)))
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
    conList.append(Sketcher.Constraint('DistanceX',0,1,0,2,width))
    conList.append(Sketcher.Constraint('DistanceY',1,2,1,1,height))
    conList.extend(extraConList)
    getattr(App.activeDocument(), sketchName).addConstraint(conList)
    App.ActiveDocument.recompute()
    getattr(App.activeDocument(), bodyName).newObject("PartDesign::Pad", padName)
    getattr(App.activeDocument(), padName).Profile = getattr(App.activeDocument(), sketchName)
    getattr(App.activeDocument(), padName).Length = depth
    getattr(App.activeDocument(), padName).Length2 = 100.000000
    getattr(App.activeDocument(), padName).Type = 0
    getattr(App.activeDocument(), padName).UpToFace = None
    getattr(App.activeDocument(), padName).Reversed = 0
    getattr(App.activeDocument(), padName).Midplane = 0
    getattr(App.activeDocument(), padName).Offset = 0.000000

    getattr(App.activeDocument(), bodyName + "_Spreadsheet").set('A1', str(width))
    getattr(App.activeDocument(), bodyName + "_Spreadsheet").set('B1', str(height))

    App.ActiveDocument.recompute()

def createBaseCabinet(name, width, height, depth, boardThickness):
    createBody(name)
    
    #create base
    createSketch(name + '_SketchBase', name, 'XY_Plane', '')
    conList = []
    conList.append(Sketcher.Constraint('Symmetric',0,1,1,2,-1,1))
    createRectangle(width, depth, boardThickness, name, name + '_SketchBase', name + '_SketchBase_Pad', conList)

    #create left side
    createSketch(name + '_SketchLeftSide', name, name + '_SketchBase_Pad', 'Face6')
    conList = []
    conList.append(Sketcher.Constraint('Distance',-1,1,3,width/2))
    conList.append(Sketcher.Constraint('DistanceY',-1,1,0,1,depth/2))
    createRectangle(boardThickness, depth, height, name, name + '_SketchLeftSide', name + '_SketchLeftSide_Pad', conList)

    #create right side
    createSketch(name + '_SketchRightSide', name, name + '_SketchBase_Pad', 'Face6')
    conList = []
    conList.append(Sketcher.Constraint('Distance',-1,1,1,width/2))
    conList.append(Sketcher.Constraint('DistanceY',-1,1,0,1,depth/2))
    createRectangle(boardThickness, depth, height, name, name + '_SketchRightSide', name + '_SketchRightSide_Pad', conList)

    #create front up
    createSketch(name + '_SketchFrontUp', name, name + '_SketchLeftSide_Pad', 'Face9')
    conList = []
    conList.append(Sketcher.Constraint('Distance',-1,1,3,depth/2))
    conList.append(Sketcher.Constraint('DistanceY',-1,1,0,1,height + boardThickness))
    createRectangle(100, boardThickness, width-2*boardThickness, name, name + '_SketchFrontUp', name + '_SketchFrontUp_Pad', conList)

    #create back up
    createSketch(name + '_SketchBackUp', name, name + '_SketchLeftSide_Pad', 'Face9')
    conList = []
    conList.append(Sketcher.Constraint('Distance',-1,1,1,depth/2))
    conList.append(Sketcher.Constraint('DistanceY',-1,1,0,1,height + boardThickness))
    createRectangle(100, boardThickness, width-2*boardThickness, name, name + '_SketchBackUp', name + '_SketchBackUp_Pad', conList)

    #create back
    createSketch(name + '_SketchBack', name, name + '_SketchBase_Pad', 'Face1')
    conList = []
    conList.append(Sketcher.Constraint('Symmetric',0,1,1,2,-1,1))
    createRectangle(width, height, 3, name, name + '_SketchBack', name + '_SketchBack_Pad', conList)

createBaseCabinet("BottlesLeft", 300, 750, 520, 18)
