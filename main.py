# VTK - Labo 4 - Scanner d'un genou
# Author : Sathiya Kirushnapillai, Mathieu Monteverde

import math
import vtk
from vtk.util.colors import white

def load_slc(filename):
    """ Load a slc file and return its content
    Args:
        source: Path and filename
    Returns:
        vtkSLCReader
    """

    slc = vtk.vtkSLCReader()
    slc.SetFileName(filename)
    slc.Update()

    return slc


def create_outline(algorithmOutput, color):
    """ Create an outline with a given Algorithm output
    Args:
        algorithmOutput: vtkAlgorithmOutput
        color (x,y,z): Color of the outline
    Returns:
        vtkActor
    """

    outline = vtk.vtkOutlineFilter()
    outline.SetInputConnection(algorithmOutput.GetOutputPort())
    outlineMapper = vtk.vtkPolyDataMapper()
    outlineMapper.SetInputConnection(outline.GetOutputPort())
    outlineActor = vtk.vtkActor()
    outlineActor.SetMapper(outlineMapper)
    outlineActor.GetProperty().SetColor(color);

    return outlineActor


def tube(reader):

    # Contouring for the skin
    mcSkin = vtk.vtkMarchingCubes()
    mcSkin.SetInputConnection(reader.GetOutputPort())
    mcSkin.SetNumberOfContours(1)
    mcSkin.SetValue(0, 50)

    # Contouring for the bones
    mcBone = vtk.vtkMarchingCubes()
    mcBone.SetInputConnection(reader.GetOutputPort())
    mcBone.SetNumberOfContours(1)
    mcBone.SetValue(0, 75)

    # Create a sphere for clipping
    sphere = vtk.vtkSphere()
    sphere.SetCenter(80, 20, 120)
    sphere.SetRadius(60)

    # Clip skin with a sphere
    clipper = vtk.vtkClipPolyData()
    clipper.SetInputConnection(mcSkin.GetOutputPort())
    clipper.SetClipFunction(sphere)
    clipper.SetValue(1)
    clipper.Update()

    bounds = mcSkin.GetOutput().GetBounds()

    # Plan
    plane = vtk.vtkPlane()
    plane.SetNormal(0, 0, 1)
    plane.SetOrigin((bounds[1] + bounds[0]) / 2.0,
                    (bounds[3] + bounds[2]) / 2.0,
                    bounds[4]);

    # Create cutter
    high = plane.EvaluateFunction((bounds[1] + bounds[0]) / 2.0,
                                  (bounds[3] + bounds[2]) / 2.0,
                                   bounds[5]);

    # Create cutter
    cutter = vtk.vtkCutter()
    cutter.SetCutFunction(plane)
    cutter.SetInputConnection(mcSkin.GetOutputPort())
    cutter.GenerateValues(18, .99, .99 * high);

    # Stripper
    stripper = vtk.vtkStripper()
    stripper.SetInputConnection(cutter.GetOutputPort())
    stripper.Update();

    tubeFilter = vtk.vtkTubeFilter()
    tubeFilter.SetInputConnection(stripper.GetOutputPort())
    tubeFilter.SetRadius(.5)
    tubeFilter.SetNumberOfSides(50)

    mapperSkin = vtk.vtkDataSetMapper()
    mapperSkin.SetInputConnection(tubeFilter.GetOutputPort())
    mapperSkin.ScalarVisibilityOff()

    mapperBone = vtk.vtkDataSetMapper()
    mapperBone.SetInputConnection(mcBone.GetOutputPort())
    mapperBone.ScalarVisibilityOff()

    actorSkin = vtk.vtkActor()
    actorSkin.SetMapper(mapperSkin)
    actorSkin.GetProperty().SetColor(0.95, 0.64, 0.64)

    actorBone = vtk.vtkActor()
    actorBone.SetMapper(mapperBone)
    actorBone.GetProperty().SetColor(0.9, 0.9, 0.9)

    assembly = vtk.vtkAssembly()
    assembly.AddPart(actorSkin)
    assembly.AddPart(actorBone)

    return assembly



def normal(reader):

    # Contouring for the skin
    mcSkin = vtk.vtkMarchingCubes()
    mcSkin.SetInputConnection(reader.GetOutputPort())
    mcSkin.SetNumberOfContours(1)
    mcSkin.SetValue(0, 50)

    # Contouring for the bones
    mcBone = vtk.vtkMarchingCubes()
    mcBone.SetInputConnection(reader.GetOutputPort())
    mcBone.SetNumberOfContours(1)
    mcBone.SetValue(0, 75)

    # Create a sphere for clipping
    sphere = vtk.vtkSphere()
    sphere.SetCenter(80, 20, 120)
    sphere.SetRadius(60)

    theSphere = vtk.vtkImplicitBoolean()
    theSphere.SetOperationTypeToDifference()
    theSphere.AddFunction(sphere)

    theSphereSample = vtk.vtkSampleFunction()
    theSphereSample.SetImplicitFunction(theSphere)
    theSphereSample.SetModelBounds(-1000, 1000, -1000, 1000, -1000, 1000)
    theSphereSample.SetSampleDimensions(120, 120, 120)
    theSphereSample.ComputeNormalsOff()
    theSphereSurface = vtk.vtkContourFilter()
    theSphereSurface.SetInputConnection(theSphereSample.GetOutputPort())
    theSphereSurface.SetValue(0, 0.0)
    mapperSphere = vtk.vtkPolyDataMapper()
    mapperSphere.SetInputConnection(theSphereSurface.GetOutputPort())
    mapperSphere.ScalarVisibilityOff()
    actorSphere = vtk.vtkActor()
    actorSphere.SetMapper(mapperSphere)
    actorSphere.GetProperty().SetColor(white)
    actorSphere.GetProperty().SetOpacity(0.1)

    # Clip skin with a sphere
    clipper = vtk.vtkClipPolyData()
    clipper.SetInputConnection(mcSkin.GetOutputPort())
    clipper.SetClipFunction(sphere)
    clipper.SetValue(1)
    clipper.Update()

    mapperSkin = vtk.vtkDataSetMapper()
    mapperSkin.SetInputConnection(clipper.GetOutputPort())
    mapperSkin.ScalarVisibilityOff()

    mapperBone = vtk.vtkDataSetMapper()
    mapperBone.SetInputConnection(mcBone.GetOutputPort())
    mapperBone.ScalarVisibilityOff()

    actorSkin = vtk.vtkActor()
    actorSkin.SetMapper(mapperSkin)
    actorSkin.GetProperty().SetColor(0.95, 0.64, 0.64)

    actorBone = vtk.vtkActor()
    actorBone.SetMapper(mapperBone)
    actorBone.GetProperty().SetColor(0.9, 0.9, 0.9)

    assembly = vtk.vtkAssembly()
    assembly.AddPart(actorSkin)
    assembly.AddPart(actorBone)
    assembly.AddPart(actorSphere)

    return assembly


def colorBones(reader):

    # Contouring for the skin
    mcSkin = vtk.vtkMarchingCubes()
    mcSkin.SetInputConnection(reader.GetOutputPort())
    mcSkin.SetNumberOfContours(1)
    mcSkin.SetValue(0, 50)
    mcSkin.Update()

    # Contouring for the bones
    mcBone = vtk.vtkMarchingCubes()
    mcBone.SetInputConnection(reader.GetOutputPort())
    mcBone.SetNumberOfContours(1)
    mcBone.SetValue(0, 75)
    mcBone.Update()

    distanceFilter = vtk.vtkDistancePolyDataFilter()
    distanceFilter.SetInputData(0, mcBone.GetOutput())
    distanceFilter.SetInputData(1, mcSkin.GetOutput())
    distanceFilter.Update()

    mapper = vtk.vtkPolyDataMapper()
    lut = mapper.GetLookupTable()
    lut.SetHueRange(2/3, 0)
    lut.Build()
    mapper.SetInputConnection(distanceFilter.GetOutputPort())
    mapper.SetScalarRange(
        distanceFilter.GetOutput().GetPointData().GetScalars().GetRange()[0],
        distanceFilter.GetOutput().GetPointData().GetScalars().GetRange()[1]
    )




    mapperBone = vtk.vtkDataSetMapper()
    mapperBone.SetInputConnection(mcBone.GetOutputPort())
    mapperBone.ScalarVisibilityOff()

    actorBone = vtk.vtkActor()
    actorBone.SetMapper(mapper)
    actorBone.GetProperty().SetColor(0.9, 0.9, 0.9)

    assembly = vtk.vtkAssembly()
    assembly.AddPart(actorBone)

    return assembly



def main():
    print("VTK Labo 4")

    FILENAME = "data/vw_knee.slc"

    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 780

    NB_RENDERER = 4

    # Load SLC file
    reader = load_slc(FILENAME)


    actor = [tube(reader), normal(reader), normal(reader), colorBones(reader)]
    outline = create_outline(reader, (0,0,0))


    # Camera
    camera = vtk.vtkCamera()
    camera.SetPosition(0, 0, 30)
    camera.Elevation(-100)
    camera.Azimuth(0)
    camera.SetRoll(180)
    camera.SetFocalPoint(0,0,0)


    # Create the Renderers
    renderers = []
    RENDERERS_COLORS = [
        [1, 0.83, 0.83],
        [0.83, 1, 0.83],
        [0.83, 0.83, 1],
        [0.83, 0.83, 0.83]
    ]

    for i in range(0, NB_RENDERER):
        r = vtk.vtkRenderer()
        # r.SetBackground(RENDERERS_COLORS[i][0], RENDERERS_COLORS[i][1], RENDERERS_COLORS[i][2])

        r.SetBackground(1, 1, 1)

        x = 0 if i % 2 == 0 else 0.5
        y = (1 - 0.5 * (i // 2)) - 0.5
        r.SetViewport(x, y, x + 0.5, y + 0.5)

        r.AddActor(actor[i])
        r.AddActor(outline)

        r.SetActiveCamera(camera)
        r.ResetCamera()

        renderers.append(r)

    # Create the RenderWindow
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.SetSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    for i in range(0, NB_RENDERER):
        renderWindow.AddRenderer(renderers[i])

    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    # Here we specify a particular interactor style.
    style = vtk.vtkInteractorStyleTrackballCamera()
    renderWindowInteractor.SetInteractorStyle(style)

    # Start
    renderWindow.Render()
    renderWindowInteractor.Start()


if __name__ == "__main__":
   main()
