let note_config = {}

function apply_multicolumn(column_count) {
    let fields = document.querySelectorAll('.fields  .field-container');
    // First load has a race condition. Keep trying until fields appear.
    // Seems to take <5ms so 20ms should be safe
    if (fields.length == 0) {
        setTimeout(() => {apply_multicolumn(column_count)}, 20)
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
        if (note_config[i] == 0) {
            field.style.gridColumn = '1/-1';
            pending.push(field);
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
}