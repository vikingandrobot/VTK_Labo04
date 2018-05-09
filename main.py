# VTK - Labo 4 - Scanner d'un genou
# Author : Sathiya Kirushnapillai, Mathieu Monteverde

import math
import sys

import vtk
from vtk.util.colors import white
import os.path


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
    outlineActor.GetProperty().SetColor(color)

    return outlineActor


def tube(reader, mcBone, mcSkin):
    """ Create the tube visualisation of the skin. The distance between each
        tube is 1cm.
    Args:
        reader: vtkSLCReader used to read the raw scanner data
        mcBone: vtkMarchingCubes used to create the bone
        mcSkin: vtkMarchingCubes used to create the skin
    Returns:
        vtkAssembly
    """

    bounds = mcSkin.GetOutput().GetBounds()

    # Plan
    plane = vtk.vtkPlane()
    plane.SetNormal(0, 0, 1)
    plane.SetOrigin((bounds[1] + bounds[0]) / 2.0,
                    (bounds[3] + bounds[2]) / 2.0,
                    bounds[4])

    high = plane.EvaluateFunction((bounds[1] + bounds[0]) / 2.0,
                                  (bounds[3] + bounds[2]) / 2.0,
                                   bounds[5])

    # Get the number and size of voxel (Axis:z)
    nbVoxelZ = reader.GetDataExtent()[5]
    sizeVoxelZ = reader.GetDataSpacing()[2]

    # Create the tubes with vtkCutter and vtkTubeFilter
    cutter = vtk.vtkCutter()
    cutter.SetCutFunction(plane)
    cutter.SetInputConnection(mcSkin.GetOutputPort())
    cutter.GenerateValues(math.floor(nbVoxelZ * sizeVoxelZ / 10) + 1, 0, high)

    tubeFilter = vtk.vtkTubeFilter()
    tubeFilter.SetInputConnection(cutter.GetOutputPort())
    tubeFilter.SetRadius(.5)
    tubeFilter.SetNumberOfSides(50)

    # Skin mapper and actor
    mapperSkin = vtk.vtkDataSetMapper()
    mapperSkin.SetInputConnection(tubeFilter.GetOutputPort())
    mapperSkin.ScalarVisibilityOff()
    actorSkin = vtk.vtkActor()
    actorSkin.SetMapper(mapperSkin)
    actorSkin.GetProperty().SetColor(0.95, 0.64, 0.64)

    # Bone mapper and actor
    mapperBone = vtk.vtkDataSetMapper()
    mapperBone.SetInputConnection(mcBone.GetOutputPort())
    mapperBone.ScalarVisibilityOff()
    actorBone = vtk.vtkActor()
    actorBone.SetMapper(mapperBone)
    actorBone.GetProperty().SetColor(0.9, 0.9, 0.9)

    # Group the actors
    assembly = vtk.vtkAssembly()
    assembly.AddPart(actorSkin)
    assembly.AddPart(actorBone)

    return assembly


def semiTransparent(mcBone, mcSkin):
    """ Create the semi-transparent visualisation of the skin. A sphere is
        clipping the skin near the articulation and the front face (as seen
        from the camera) of the skin is semi-transparent.
    Args:
        mcBone: vtkMarchingCubes used to create the bone
        mcSkin: vtkMarchingCubes used to create the skin
    Returns:
        vtkAssembly
    """

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

    # Skin mapper
    mapperSkin = vtk.vtkDataSetMapper()
    mapperSkin.SetInputConnection(clipper.GetOutputPort())
    mapperSkin.ScalarVisibilityOff()

    # Opaque back skin
    actorSkinBack = vtk.vtkActor()
    actorSkinBack.SetMapper(mapperSkin)
    actorSkinBack.GetProperty().SetColor(0.95, 0.64, 0.64)
    actorSkinBack.GetProperty().SetFrontfaceCulling(True)

    # Transparent front skin
    actorSkinFront = vtk.vtkActor()
    actorSkinFront.SetMapper(mapperSkin)
    actorSkinFront.GetProperty().SetColor(0.95, 0.64, 0.64)
    actorSkinFront.GetProperty().SetBackfaceCulling(True)
    actorSkinFront.GetProperty().SetOpacity(0.5)

    # Bone mapper and actor
    mapperBone = vtk.vtkDataSetMapper()
    mapperBone.SetInputConnection(mcBone.GetOutputPort())
    mapperBone.ScalarVisibilityOff()
    actorBone = vtk.vtkActor()
    actorBone.SetMapper(mapperBone)
    actorBone.GetProperty().SetColor(0.9, 0.9, 0.9)

    # Group the actors
    assembly = vtk.vtkAssembly()
    assembly.AddPart(actorSkinBack)
    assembly.AddPart(actorSkinFront)
    assembly.AddPart(actorBone)

    return assembly


def normal(mcBone, mcSkin):
    """ Create the default visualisation of the skin. A sphere is
        clipping the skin near the articulation and is slightly visible using
        a low opacity.
    Args:
        mcBone: vtkMarchingCubes used to create the bone
        mcSkin: vtkMarchingCubes used to create the skin
    Returns:
        vtkAssembly
    """

    # Create a sphere for clipping
    sphere = vtk.vtkSphere()
    sphere.SetCenter(80, 20, 120)
    sphere.SetRadius(60)

    theSphere = vtk.vtkImplicitBoolean()
    theSphere.SetOperationTypeToDifference()
    theSphere.AddFunction(sphere)

    # Display the sphere
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

    # Skin mapper and actor
    mapperSkin = vtk.vtkDataSetMapper()
    mapperSkin.SetInputConnection(clipper.GetOutputPort())
    mapperSkin.ScalarVisibilityOff()
    actorSkin = vtk.vtkActor()
    actorSkin.SetMapper(mapperSkin)
    actorSkin.GetProperty().SetColor(0.95, 0.64, 0.64)

    # Bone mapper and actor
    mapperBone = vtk.vtkDataSetMapper()
    mapperBone.SetInputConnection(mcBone.GetOutputPort())
    mapperBone.ScalarVisibilityOff()
    actorBone = vtk.vtkActor()
    actorBone.SetMapper(mapperBone)
    actorBone.GetProperty().SetColor(0.9, 0.9, 0.9)

    # Group the actors
    assembly = vtk.vtkAssembly()
    assembly.AddPart(actorSkin)
    assembly.AddPart(actorBone)
    assembly.AddPart(actorSphere)

    return assembly


def colorBones(mcBone, mcSkin):
    """ Create the colored distance visualisation of the bone to the skin.
        The bone is colored from blue (far) to red (close) based on its
        distance to the skin. This function looks for a file named
        'distanceFilter.vtk' in the current directory and if it exists, it
        reads the necessary data from it (thus saving a processing time).
        If the file is not to be found, the script processes the distances and
        saves the result in a file with the same name as above.
    Args:
        mcBone: vtkMarchingCubes used to create the bone
        mcSkin: vtkMarchingCubes used to create the skin
    Returns:
        vtkAssembly
    """

    SAVED_DISTANCE_FILEPATH = './distanceFilter.vtk'

    # Get the distance between the bone and the skin
    # If a saved file already exists, use iter
    distanceFilter = vtk.vtkDistancePolyDataFilter()
    if (os.path.isfile(SAVED_DISTANCE_FILEPATH)):
        # Read from saved file
        reader = vtk.vtkPolyDataReader()
        reader.SetFileName(SAVED_DISTANCE_FILEPATH)
        reader.Update()
        input = reader.GetOutput()

        distanceFilter = vtk.vtkCleanPolyData()
        distanceFilter.SetInputData(input)
    else:
        # Compute the data
        distanceFilter.SetInputData(0, mcBone.GetOutput())
        distanceFilter.SetInputData(1, mcSkin.GetOutput())
        distanceFilter.Update()

        # Save to file
        writer = vtk.vtkPolyDataWriter()
        writer.SetInputConnection(distanceFilter.GetOutputPort()	)
        writer.SetFileName(SAVED_DISTANCE_FILEPATH)
        writer.Update()

    # Update
    distanceFilter.Update()

    mapper = vtk.vtkPolyDataMapper()

    # Set the coloring range
    lut = mapper.GetLookupTable()
    lut.SetHueRange(2/3, 0)
    lut.Build()

    # Apply the color
    mapper.SetInputConnection(distanceFilter.GetOutputPort())
    mapper.SetScalarRange(
        distanceFilter.GetOutput().GetPointData().GetScalars().GetRange()[0],
        distanceFilter.GetOutput().GetPointData().GetScalars().GetRange()[1]
    )

    actorBone = vtk.vtkActor()
    actorBone.SetMapper(mapper)
    actorBone.GetProperty().SetColor(0.9, 0.9, 0.9)

    # Group the actors
    assembly = vtk.vtkAssembly()
    assembly.AddPart(actorBone)

    return assembly


def main():
    """ This main function reads raw scanner data of a knee and create four
        visualisations inside a window. The visualisations are detailed
        in the 'tube', 'semiTransperent', 'normal' and 'colorBones' functions.
        The input file is the first argument of the script.
        
        Usage example: python main.py data/vw_knee.slc
    """
    if (len(sys.argv) != 2):
        print("Usage: python main.py <path to raw scanner data file>")
        sys.exit()

    FILENAME = sys.argv[1]

    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 780

    NB_RENDERER = 4

    # Load SLC file
    reader = load_slc(FILENAME)

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

    actor = [
        tube(reader, mcBone, mcSkin),
        semiTransparent(mcBone, mcSkin),
        normal(mcBone, mcSkin),
        colorBones(mcBone, mcSkin)
    ]

    outline = create_outline(reader, (0, 0, 0))

    # Camera
    camera = vtk.vtkCamera()
    camera.SetPosition(0, 0, 30)
    camera.Elevation(-100)
    camera.Azimuth(0)
    camera.SetRoll(180)
    camera.SetFocalPoint(0, 0, 0)

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
        r.SetBackground(RENDERERS_COLORS[i][0], RENDERERS_COLORS[i][1], RENDERERS_COLORS[i][2])

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
