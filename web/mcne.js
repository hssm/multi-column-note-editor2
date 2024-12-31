let note_config = {}

function apply_multicolumn() {
    let column_count = note_config['column_count'];
    let field_sizes = note_config['field_sizes'];
    let fields = document.querySelectorAll('.fields  .field-container');

    // First load has a race condition. Keep trying until fields appear.
    // Seems to take <5ms so 20ms should be safe
    if (fields.length == 0) {
        setTimeout(() => {apply_multicolumn()}, 20)
        return;
    }

    let grid = document.querySelector('.fields');
    grid.style.display = "grid";
    grid.style.gridTemplateColumns = "repeat("+column_count+", minmax(0, 1fr))";

    let pending = [];
    let allocated = 0;
    let idx = 0;
    for(let i = 0; i < fields.length; i++) {
        let field = fields[i];
        let size = field_sizes[i];
        field.setAttribute('mcne-idx', i);
        field.style.gridColumn = 'unset';
        add_expander(field, size);
        // Set height inside shadow root - can't do it in css
        let shadow = field.querySelector('.rich-text-editable').shadowRoot;
        shadow.querySelector('anki-editable').style.height = "100%";

        // Size=0 means expand to fill line. Skip in 1-column mode
        if (size == 0 && column_count > 1) {
            field.style.gridColumn = '1/-1';
            if (allocated == 0) {
                // If we're expanding column 0, make that the line immediately
                // It feels much nicer and more predictable that way
                field.style.order = idx++;
            } else {
                pending.push(field);
            }
            continue
        }

        field.style.order = idx++;
        allocated++;

        if (allocated == column_count) {
            allocated = 0;
            pending.forEach((pfield) => pfield.style.order = idx++);
            pending = [];
        }
    }
    // If we finished with unallocated fields, add them to the end
    pending.forEach((pfield) => pfield.style.order = idx++);
}

function add_expander(field, size) {
    field.setAttribute('mcne-size', size);
    // Reuse or make new expander
    let expander = field.querySelector('.field-state .mcne-expander');
    if (expander == null) {
        expander = document.createElement('span');
        expander.classList.add('mcne-expander');
        expander.addEventListener('click', on_expand);
    }
    if (!size) {
        expander.innerHTML = '⥃';
        expander.setAttribute('expanded', true);
    } else {
        expander.innerHTML = '⥂ ';
        expander.setAttribute('expanded', false);
    }
    field.querySelector('.field-state').prepend(expander);
}

function on_expand(event) {
    let expander = event.target;
    let field = expander.closest('.field-container');
    let idx = field.getAttribute('mcne-idx');
    let size = field.getAttribute('mcne-size');
    size = size == "0" ? 1 : 0;
    pycmd('MCNE:' + JSON.stringify({'idx': idx, 'size': size}));
}