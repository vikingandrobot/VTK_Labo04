import vtk

FILEPATH = "../data/vw_knee.slc"

reader = vtk.vtkSLCReader()
reader.SetFileName(FILEPATH)
reader.Update()

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

mapperSkin = vtk.vtkDataSetMapper()
mapperSkin.SetInputConnection(mcSkin.GetOutputPort())
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

renderer = vtk.vtkRenderer()
renderer.AddActor(actorSkin)
renderer.AddActor(actorBone)
renderer.SetBackground(0.3, 0.6, 0.3)

renderWindow = vtk.vtkRenderWindow()
renderWindow.SetSize(1200, 720)
renderWindow.AddRenderer(renderer)
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

# Here we specify a particular interactor style.
style = vtk.vtkInteractorStyleTrackballCamera()
renderWindowInteractor.SetInteractorStyle(style)

renderWindow.Render()
renderWindowInteractor.Start()
