function move_row(e, up) {
    var row = $(e).closest('tr');
    if (up)
      row.prev().before(row);
    else
      row.next().after(row);
  }

function delete_row(e) {
    var row = $(e).closest('tr');
    row.remove();
  }

function open_popup (url, width=700, height=400) {
    window.open(url,"_blank","width=700,height=400") ;
  }

