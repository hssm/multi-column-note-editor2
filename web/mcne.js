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

    let cols = Array(column_count).fill('auto');
    let grid = document.querySelector('.fields');
    grid.style.display = "grid";
    grid.style.gridTemplateColumns = cols.join(' ');

    let pending = [];
    let allocated = 0;
    let idx = 0;

    for(let i = 0; i < fields.length; i++) {
        let field = fields[i];
        field.setAttribute('mcne-idx', i);
        // Size=0 means expand to fill line
        if (field_sizes[i] == 0) {
            field.style.gridColumn = '1/-1';
            // Don't defer in 1-column mode. Order as we see them
            if (column_count > 1) {
                pending.push(field);
                continue
            }
        }

        field.style.order = idx++;
        field.setAttribute('tabindex', idx);
        allocated++;

        if (allocated == column_count) {
            allocated = 0;
            pending.forEach((pfield) => pfield.style.order = idx++);
            pending = [];
        }
    }
}