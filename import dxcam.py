import dxcam

print(dxcam.device_info())
print(dxcam.output_info())

camera = dxcam.create( backend="dxgi",device_idx=0, output_idx=0)
camera.release()
print(camera)