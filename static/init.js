document.addEventListener('DOMContentLoaded', function () {
    const elems = document.querySelectorAll('select');
    M.FormSelect.init(elems, null);
});

document.addEventListener('DOMContentLoaded', function () {
    const elems = document.querySelectorAll('.collapsible');
    M.Collapsible.init(elems, null);
});

init_dates = function (fromDate, untilDate) {
    const from = document.querySelector('#from_date');
    const from_options = {
        format: "d mmm yyyy",
        firstDay: 1,

        defaultDate: fromDate,
        setDefaultDate: true
    }
    M.Datepicker.init(from, from_options);
    const until = document.querySelector('#until_date');
    const until_options = {
        format: "d mmm yyyy",
        firstDay: 1,

        defaultDate: untilDate,
        setDefaultDate: true
    }
    M.Datepicker.init(until, until_options);
}

document.addEventListener('DOMContentLoaded', _ => init_dates(defaultFromDate, defaultUntilDate));

$('#sort_by').change(function () {
    let url = new URL(window.location.href)
    url.searchParams.set("sort", $(this).val())
    window.location.href = url.toString()
})

$('#reset-date').click(function () {
    init_dates(firstIssueDate, today);
})
