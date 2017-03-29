# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, 2016
#
# ##### END LICENSE BLOCK #####

bl_info = {
    "name": "Re-Volt PRM Import/Export",
    "author": "Dummiesman",
    "version": (0, 0, 1),
    "blender": (2, 78, 0),
    "location": "File > Import-Export",
    "description": "Import-Export PRM files",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.7/Py/"
                "Scripts/Import-Export/DummiesmanPRM",
    "support": 'COMMUNITY',
    "category": "Import-Export"}

import bpy
from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        StringProperty,
        CollectionProperty,
        )
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        )

class ImportPRM(bpy.types.Operator, ImportHelper):
    """Import from PRM file format (.prm)"""
    bl_idname = "import_scene.prm"
    bl_label = 'Import PRM'
    bl_options = {'UNDO'}

    filename_ext = ".prm"
    filter_glob = StringProperty(default="*.prm", options={'HIDDEN'})

    def execute(self, context):
        from . import import_prm
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            "check_existing",
                                            ))

        return import_prm.load(self, context, **keywords)


class ExportPRM(bpy.types.Operator, ExportHelper):
    """Export to PRM file format (.prm)"""
    bl_idname = "export_scene.prm"
    bl_label = 'Export PRM'

    filename_ext = ".prm"
    filter_glob = StringProperty(
            default="*.prm",
            options={'HIDDEN'},
            )
        
    def execute(self, context):
        from . import export_prm
        
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            "check_existing",
                                            ))
                                    
        return export_prm.save(self, context, **keywords)


# Add to a menu
def menu_func_export(self, context):
    self.layout.operator(ExportPRM.bl_idname, text="Re-Volt PRM (.prm)")


def menu_func_import(self, context):
    self.layout.operator(ImportPRM.bl_idname, text="Re-Volt PRM (.prm)")


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()