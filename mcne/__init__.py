import json

import aqt.editor
from aqt import *
from aqt.editor import Editor
from aqt.webview import WebContent

addon_package = mw.addonManager.addon_from_module(__name__)

class MCNE:
    def __init__(self):
        self.cc_spin = None
        self.editor = None

    def on_webview_will_set_content(self, web_content: WebContent, context):
        if not isinstance(context, Editor):
            return
        web_content.js.append(f"/_addons/{addon_package}/web/mcne.js")
        web_content.css.append(f"/_addons/{addon_package}/web/mcne.css")

    def did_load_note(self, editor, focusTo=None) -> None:
        count = 3  # TODO:
        config = json.dumps({
            0: 1,
            1: 0,
            2: 1,
            3: 1,
            4: 1,
            5: 1
        })

        editor.web.eval(f"note_config = {config}")
        editor.web.eval(f"apply_multicolumn({count})")

    def editor_init(self, editor):
        self.editor = editor
        self.cc_spin = QSpinBox(editor.widget)
        hbox = QHBoxLayout()
        spacer = QLabel("", editor.widget)
        label = QLabel("Columns:", editor.widget)
        hbox.addWidget(spacer)
        hbox.addStretch()
        hbox.addWidget(label)
        hbox.addWidget(self.cc_spin)

        self.cc_spin.setMinimum(1)
        self.cc_spin.setMaximum(18)
        self.cc_spin.valueChanged.connect(
            lambda count: self.on_column_count_changed(editor, count)
        )
        editor.outerLayout.addLayout(hbox)

    def on_column_count_changed(self, editor, count):
        editor.web.eval(f"apply_multicolumn({count})")


    def getKeyForContext(self, field=None):
        return str(self.editor.note.mid)


mw.addonManager.setWebExports(__name__, r"web/.*")
mcne = MCNE()

gui_hooks.webview_will_set_content.append(mcne.on_webview_will_set_content)
gui_hooks.editor_did_load_note.append(mcne.did_load_note)
gui_hooks.editor_did_init.append(mcne.editor_init)
