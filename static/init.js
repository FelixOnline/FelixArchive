document.addEventListener('DOMContentLoaded', function() {
  const elems = document.querySelectorAll('select');
  M.FormSelect.init(elems, null);
});

$('#sort_by').change(function(){
  let url  = new URL(window.location.href)
  url.searchParams.set("sort", $(this).val())
  window.location.href = url.toString()
})
