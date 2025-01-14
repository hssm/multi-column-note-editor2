# https://github.com/hssm/multi-column-note-editor2
# Version 1.2

import json

from aqt import *
from aqt.editor import Editor
from aqt.webview import WebContent

addon_package = mw.addonManager.addon_from_module(__name__)
instances = {}

class MCNE:
    def __init__(self, editor):
        self.note_config = None
        self.editor = editor
        self.cc_spin = QSpinBox(editor.widget)
        self.cc_spin.setFixedWidth(50)
        hbox = QHBoxLayout()
        spacer = QLabel("", editor.widget)
        label = QLabel("Columns:", editor.widget)
        hbox.addWidget(spacer)
        hbox.addStretch()
        hbox.addWidget(label)
        hbox.addWidget(self.cc_spin)

        self.cc_spin.setMinimum(1)
        self.cc_spin.setMaximum(50)
        self.cc_spin.valueChanged.connect(
            lambda count: self.on_column_count_changed(count)
        )
        editor.outerLayout.addLayout(hbox)

    def save_config(self):
        config = mw.col.get_config('mcne', dict())
        mid = str(self.editor.note.mid)
        config[mid] = self.note_config
        mw.col.set_config('mcne', config)

    def load_note_config(self):
        config = mw.col.get_config('mcne', dict())
        note_config = config.get(str(self.editor.note.mid), {
            'column_count': 1,
            'field_sizes': []
        })
        # Ensure the config has an index for each field in the note
        missing = len(self.editor.note.fields) - len(note_config['field_sizes'])
        for m in range(0, missing):
            note_config['field_sizes'].append(1)
        self.note_config = note_config

    def apply_multicolumn(self):
        self.editor.web.eval(f"note_config = {json.dumps(self.note_config)}")
        self.editor.web.eval(f"mcne_id = {json.dumps(id(self))}")
        self.editor.web.eval(f"apply_multicolumn()")

    def on_column_count_changed(self, count):
        instance_cleanup()
        # Apply change to all open editors with this note type
        for mcne in instances.values():
            if mcne.editor.note and mcne.editor.note.mid == self.editor.note.mid:
                mcne.note_config['column_count'] = count
                mcne.save_config()
                mcne.apply_multicolumn()

def _new_editor(editor):
    mcne = MCNE(editor)
    instances[editor] = mcne

def on_webview_will_set_content(web_content: WebContent, context):
    if not isinstance(context, Editor):
        return
    web_content.js.append(f"/_addons/{addon_package}/web/mcne.js")
    web_content.css.append(f"/_addons/{addon_package}/web/mcne.css")

def did_load_note(editor, focusTo=None):
    instance_cleanup()
    for mcne in instances.values():
        if mcne.editor == editor:
            mcne.load_note_config()
            mcne.cc_spin.setValue(mcne.note_config['column_count'])
            mcne.apply_multicolumn()

def on_js_message(handled, message, context):
    if not message.startswith('MCNE:'):
        return handled

    instance_cleanup()

    # Apply change to all open editors with this note type
    vals = json.loads(message[5:])
    mid = None
    for mcne in instances.values():
        if vals['mcne_id'] == id(mcne):
            mid = mcne.editor.note.mid
    for mcne in instances.values():

        if mcne.editor.note and mcne.editor.note.mid == mid:
            mcne.note_config['field_sizes'][int(vals['idx'])] = vals['size']
            mcne.save_config()
            mcne.apply_multicolumn()
    return True, None

def instance_cleanup():
    remove = []
    for editor in instances:
        if editor.parentWindow not in aqt.DialogManager._dialogs[editor.parentWindow.__class__.__name__]:
            remove.append(editor)
    for editor in remove:
        del instances[editor]


mw.addonManager.setWebExports(__name__, r"web/.*")

gui_hooks.editor_did_init.append(_new_editor)
gui_hooks.webview_will_set_content.append(on_webview_will_set_content)
gui_hooks.editor_did_load_note.append(did_load_note)
gui_hooks.webview_did_receive_js_message.append(on_js_message)
