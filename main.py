# VTK - Labo 4 - Scanner d'un genou
# Author : Sathiya Kirushnapillai, Mathieu Monteverde

import math
import vtk

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

    return assembly


def main():
    print("VTK Labo 4")

    FILENAME = "data/vw_knee.slc"

    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 780

    NB_RENDERER = 4

    # Load SLC file
    reader = load_slc(FILENAME)


    actor = normal(reader)


    # Camera
    camera = vtk.vtkCamera()
    camera.SetPosition(0, 0, 30)
    camera.Elevation(-100)
    camera.Azimuth(0)
    camera.SetRoll(180)
    camera.SetFocalPoint(0,0,0)   


    # Create the Renderers
    renderers = []
    for i in range(0, NB_RENDERER):
        r = vtk.vtkRenderer()
        r.SetBackground(0.95, 0.95, 0.95)

        x = 0 if i % 2 == 0 else 0.5
        y = (1 - 0.5 * (i // 2)) - 0.5
        r.SetViewport(x, y, x + 0.5, y + 0.5)

        r.AddActor(actor)

        r.SetActiveCamera(camera)
        r.ResetCamera()

        renderers.append(r)


    # Create the RenderWindow
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.SetSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)
    for i in range(0, NB_RENDERER):
        renderWindow.AddRenderer(renderers[i])


    # Start
    renderWindow.Render()
    renderWindowInteractor.Start()


if __name__ == "__main__":
   main()
