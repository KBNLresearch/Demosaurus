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

function openTab(evt, tabName){
    // Declare all variables
  var i, tabcontent, tablinks;

  // Get all elements with class="tabcontent" and hide them
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }

  // Get all elements with class="tablinks" and remove the class "active"
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }

  // Show the current tab, and add an "active" class to the button that opened the tab
  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.className += " active";

}