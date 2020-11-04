document.addEventListener('DOMContentLoaded', function () {
    const elems = document.querySelectorAll('select');
    M.FormSelect.init(elems, null);
});

document.addEventListener('DOMContentLoaded', function () {
    const elems = document.querySelectorAll('.collapsible');
    M.Collapsible.init(elems, null);
});

init_dates = function (fromDate, toDate) {
    const from = document.querySelector('#from_date');
    const from_options = {
        format: "d mmm yyyy",
        firstDay: 1,
        autoClose: true,

        yearRange: [firstIssueDate.getFullYear(), today.getFullYear()],

        defaultDate: fromDate,
        setDefaultDate: true
    }
    M.Datepicker.init(from, from_options);
    const to = document.querySelector('#to_date');
    const to_options = {
        format: "d mmm yyyy",
        firstDay: 1,
        autoClose: true,

        yearRange: [firstIssueDate.getFullYear(), today.getFullYear()],

        defaultDate: toDate,
        setDefaultDate: true
    }
    M.Datepicker.init(to, to_options);
}

document.addEventListener('DOMContentLoaded', _ => init_dates(defaultFromDate, defaultToDate));

$('#sort_by').change(function () {
    let url = new URL(window.location.href)
    url.searchParams.set("sort", $(this).val())
    window.location.href = url.toString()
})

$('#reset-date').click(function () {
    init_dates(firstIssueDate, today);
})
