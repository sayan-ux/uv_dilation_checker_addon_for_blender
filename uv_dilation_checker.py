bl_info = {
    "name": "UV Dilation Checker",
    "author": "Sayan Sikdar",
    "version": (1, 1),
    "blender": (2, 80, 0),
    "description": "check diation for uv",
    "category": "UV"
}

import bpy
from bpy.types import Operator, Panel
from bpy.props import EnumProperty, IntProperty
import tempfile
import os
import sys

sys.path.append(os.path.dirname(__file__))

import cv2
import numpy as np

class UVEditorPanel(Panel):
    bl_label = "UV dilation checker"
    bl_idname = "PT_UVEditorPanel"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "UV dilation checker"
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'


    def draw(self, context):
        layout = self.layout
        uv_editor = context.space_data
        scene = context.scene

        layout.prop(scene, "uv_resolution_option")
        layout.prop(scene, "stroke_size")
        layout.operator("uv.generate_image", text="Generate Image")

class UV_OT_GenerateImage(Operator):
    bl_label = "Generate Image"
    bl_idname = "uv.generate_image"
    
    def execute(self, context):
        
        resolution = int(context.scene.uv_resolution_option)
        strokesize = context.scene.stroke_size

        generator(resolution, strokesize)

        return {'FINISHED'}

def cv_to_bpy_image(cv_img, name):
    height, width, _channel = cv_img.shape
    bpy_image = bpy.data.images.new(name, width=width, height=height)
    bpy_image.pixels = np.flipud(cv_img.flatten())
    bpy_image.update()

    return bpy_image
def generator(resolution, strokesize):
    
    tmpdir = tempfile.gettempdir()
    resolution = resolution
    dilation = strokesize
    dilation = dilation*2
    imagename = "uv_dilation.png"

    filepath = os.path.join(tmpdir, imagename)

    bpy.ops.uv.select_all(action='SELECT')
    bpy.ops.uv.export_layout(filepath=filepath, size=(resolution, resolution), opacity=1)
    bpy.ops.uv.select_all(action='DESELECT')

    image1 = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)
    strokecolor = (0,0,0, 255)
        

    mask = (image1[:, :, 3] > 0).astype(np.uint8)

    kernel = np.ones((dilation, dilation), np.uint8)
    dilated_mask = cv2.dilate(mask, kernel, iterations=1)

    strokedimage = np.zeros_like(image1)
    strokedimage[:, :, 3] = dilated_mask * 255

    for c in range(3):
        strokedimage[:, :, c] = strokecolor[c]

    result = cv2.add(image1, strokedimage)
    
    mask = (result[:, :, 3] == 0)
    result[mask] = [255, 255, 255, 255]
    cv2.imwrite(filepath, result)

    bpy.ops.image.open(filepath=filepath, directory=tmpdir, files=[{"name":imagename}], relative_path=True, show_multiview=False)

    image = bpy.data.images[imagename]

    uveditorfound = False

    for area in bpy.context.screen.areas:
        if area.type == 'IMAGE_EDITOR':
            uveditorfound = True
            area.spaces.active.image = image
            break




def register():
    bpy.utils.register_class(UVEditorPanel)
    bpy.utils.register_class(UV_OT_GenerateImage)
    bpy.types.Scene.uv_resolution_option = EnumProperty(
        name="Resolution",
        items=[
            ('32', "32", "32 Resolution"),
            ('64', "64", "64 Resolution"),
            ('128', "128", "128 Resolution"),
            ('256', "256", "256 Resolution"),
            ('512', "512", "512 Resolution"),
            ('1024', "1024", "1K Resolution"),
            ('2048', "2048", "2K Resolution"),
            ('4096', "4096", "4K Resolution"),
            ('8192', "8192", "8K Resolution"),
        ],
    )
    bpy.types.Scene.stroke_size = IntProperty(
        name="Stroke Size",
        min=1,
        default=1,
    )

def unregister():
    bpy.utils.unregister_class(UVEditorPanel)
    bpy.utils.unregister_class(UV_OT_GenerateImage)
    del bpy.types.Scene.uv_resolution_option
    del bpy.types.Scene.stroke_size

if __name__ == "__main__":
    register()
