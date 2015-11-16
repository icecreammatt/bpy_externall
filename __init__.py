# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "bpy externall",
    "author": "Dealga McArdle",
    "version": (0, 1),
    "blender": (2, 7, 6),
    "location": "",
    "description": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Text Editor"
}


import sys
import importlib

import bpy
from bpy.props import (
    BoolProperty, StringProperty, FloatProperty
)


STOPPED = 2
RUNNING = 3

statemachine = {
    'status': STOPPED,
    'tempfile': '/home/zeffii/Desktop/IO/fp.io'
}


def empty_file_content(fp, temp_path):
    if fp.strip():
        with open(temp_path, 'w') as f:
            pass


def filepath_read_handler():
    """
    this reads the filepath io file, and returns the filepath found.
    """
    temp_path = statemachine['tempfile']

    fp = ""
    with open(temp_path) as f:
        fp = f.read()
        # print('fp: read', fp)

    empty_file_content(fp, temp_path)
    return fp.strip()


def execute_file(fp):
    texts = bpy.data.texts
    tf = 'temp_file'
    if tf in texts:
        text = texts[tf]
    else:
        text = texts.new(tf)

    text.from_string(open(fp).read())
    ctx = bpy.context.copy()
    ctx['edit_text'] = text

    try:
        bpy.ops.text.run_script(ctx)
    except Exception as err:
        sys.stderr.write('ERROR: %s\n' % str(err))
        # print(sys.exc_info()[-1].tb_frame.f_code)
        # print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))


class BPYExternallClient(bpy.types.Operator, object):

    bl_idname = "wm.bpy_externall_server"
    bl_label = "start and stop server"

    _timer = None
    speed = FloatProperty()
    mode = StringProperty()
    last_action = StringProperty()

    def process(self):
        fp = filepath_read_handler()
        # print('process: ', fp)
        if fp:
            print('-- action', fp)
            execute_file(fp)

    def modal(self, context, event):

        if statemachine['status'] == STOPPED:
            self.cancel(context)
            return {'FINISHED'}

        if not (event.type == 'TIMER'):
            return {'PASS_THROUGH'}

        self.process()
        return {'PASS_THROUGH'}

    def event_dispatcher(self, context, type_op):
        if type_op == 'start':
            statemachine['status'] = RUNNING

            wm = context.window_manager
            self._timer = wm.event_timer_add(self.speed, context.window)
            wm.modal_handler_add(self)

        if type_op == 'end':
            statemachine['status'] = STOPPED

    def execute(self, context):
        self.event_dispatcher(context, self.mode)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


class BPYExternallPanel(bpy.types.Panel):

    bl_idname = "BPYExternallPanel"
    bl_label = "bpy externall panel"
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    # bl_options = {'DEFAULT_CLOSED'}
    use_pin = True

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        state = statemachine['status']

        # promising! continue
        tstr = ''
        if state == STOPPED:
            tstr = 'start'
        elif state == RUNNING:
            col.label('listening on ' + statemachine['tempfile'])
            tstr = 'end'

        if tstr:
            op = col.operator('wm.bpy_externall_server', text=tstr)
            op.mode = tstr
            op.speed = 1


def register():
    bpy.utils.register_class(BPYExternallPanel)
    bpy.utils.register_class(BPYExternallClient)


def unregister():
    bpy.utils.unregister_class(BPYExternallPanel)
    bpy.utils.unregister_class(BPYExternallClient)
