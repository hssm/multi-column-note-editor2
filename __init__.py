# https://github.com/hssm/multi-column-note-editor2
# Version 1.1

import json

from aqt import *
from aqt.editor import Editor
from aqt.webview import WebContent

addon_package = mw.addonManager.addon_from_module(__name__)

class MCNE:
    def __init__(self):
        self.cc_spin = None
        self.editor = None
        self.note_config = None

    def editor_init(self, editor):
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

    def on_webview_will_set_content(self, web_content: WebContent, context):
        if not isinstance(context, Editor):
            return
        web_content.js.append(f"/_addons/{addon_package}/web/mcne.js")
        web_content.css.append(f"/_addons/{addon_package}/web/mcne.css")

    def did_load_note(self, editor, focusTo=None):
        self.load_note_config()
        self.cc_spin.setValue(self.note_config['column_count'])
        self.apply_multicolumn()

    def apply_multicolumn(self):
        self.editor.web.eval(f"note_config = {json.dumps(self.note_config)}")
        self.editor.web.eval(f"apply_multicolumn()")

    def on_column_count_changed(self, count):
        self.note_config['column_count'] = count
        self.save_config()
        self.apply_multicolumn()

    def on_js_message(self, handled, message, context):
        if not message.startswith('MCNE:'):
            return handled

        vals = json.loads(message[5:])
        self.note_config['field_sizes'][int(vals['idx'])] = vals['size']
        self.save_config()
        self.apply_multicolumn()
        return True, None


mw.addonManager.setWebExports(__name__, r"web/.*")
mcne = MCNE()

gui_hooks.webview_will_set_content.append(mcne.on_webview_will_set_content)
gui_hooks.editor_did_load_note.append(mcne.did_load_note)
gui_hooks.editor_did_init.append(mcne.editor_init)
gui_hooks.webview_did_receive_js_message.append(mcne.on_js_message)
