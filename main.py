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


def main():
    print("VTK Labo 4")

    FILENAME = "data/vw_knee.slc"

    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600

    NB_RENDERER = 4

    # Load SLC file
    slc = load_slc(FILENAME)


    marchingCubes = vtk.vtkMarchingCubes()
    marchingCubes.SetInputConnection(slc.GetOutputPort())
    marchingCubes.SetValue(0, 72)

    dataSetMapper = vtk.vtkDataSetMapper()
    dataSetMapper.SetInputConnection(marchingCubes.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(dataSetMapper)

    
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
