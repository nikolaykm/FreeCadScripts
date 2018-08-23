def createBody(bodyName):
    App.activeDocument().addObject('PartDesign::Body', bodyName)
    App.ActiveDocument.recompute()

def createSketch(sketchName, bodyName, supportName, supportFace):
    getattr(App.activeDocument(), bodyName).newObject('Sketcher::SketchObject', sketchName)
    getattr(App.activeDocument(), sketchName).Support = (getattr(App.activeDocument(), supportName), [supportFace])
    getattr(App.activeDocument(), sketchName).MapMode = 'FlatFace'
    App.ActiveDocument.recompute()

def createRectangle(width, height, sketchName, bodyName, padName):

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
    conList.append(Sketcher.Constraint('DistanceX',0,1,0,2,App.Units.Quantity(width)))
    conList.append(Sketcher.Constraint('DistanceY',1,2,1,1,App.Units.Quantity(height)))
    conList.append(Sketcher.Constraint('Symmetric',0,1,1,2,-1,1))
    getattr(App.activeDocument(), sketchName).addConstraint(conList)
    App.ActiveDocument.recompute()
    getattr(App.activeDocument(), bodyName).newObject("PartDesign::Pad", padName)
    getattr(App.activeDocument(), padName).Profile = getattr(App.activeDocument(), sketchName)
    getattr(App.activeDocument(), padName).Length = 18.0
    getattr(App.activeDocument(), padName).Length2 = 100.000000
    getattr(App.activeDocument(), padName).Type = 0
    getattr(App.activeDocument(), padName).UpToFace = None
    getattr(App.activeDocument(), padName).Reversed = 0
    getattr(App.activeDocument(), padName).Midplane = 0
    getattr(App.activeDocument(), padName).Offset = 0.000000
    App.ActiveDocument.recompute()

createBody('Body')
createSketch('Sketch', 'Body', 'XY_Plane', '')
createRectangle('500.000000 mm', '550.000000 mm', 'Sketch', 'Body', 'Pad')
createSketch('Sketch1', 'Body', 'Pad', 'Face6')
createRectangle('100.000000 mm', '150.000000 mm', 'Sketch1', 'Body', 'Pad1')
