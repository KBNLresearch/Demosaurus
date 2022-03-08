function move_row(e, up) {
    var row = $(e).closest('tr');
    console.log(row);
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
  document.getElementById(tabName).style.display = "block";

   // Get all elements with class="tablinks" and remove the class "active"
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }

  // Show the current tab, and add an "active" class to the button that opened the tab
  document.getElementById(tabName + "_content").style.display = "block";
  evt.currentTarget.className += " active";

}

var getColorForPercentage = function(this_perc, saturation=1.0, low=0.5) {
    var percentColors = [
    { pct: 0.0, color: { r: 255, g: 255, b: 255 } },
    { pct: low, color: { r: 247, g: 233, b: 187 } },
    { pct: 1.0, color: { r: 233, g: 195, b: 73 } } ];

    this_perc = Number(this_perc) ;
    for (var i = 1; i < percentColors.length - 1; i++) {
      if (this_perc < percentColors[i].pct) {
        break;
      }
    }
    var lower = percentColors[i - 1];
    var upper = percentColors[i];
    var range = upper.pct - lower.pct;
    var rangePct = (this_perc - lower.pct) / range;
    var pctLower = 1 - rangePct;
    var pctUpper = rangePct;
    var color = {
      r: Math.floor(lower.color.r * pctLower + upper.color.r * pctUpper),
      g: Math.floor(lower.color.g * pctLower + upper.color.g * pctUpper),
      b: Math.floor(lower.color.b * pctLower + upper.color.b * pctUpper)
    };
    return 'rgba(' + [color.r, color.g, color.b, saturation].join(',') + ')';
  };

  // DataTabel.js init interactive tables.
  $(document).ready( function () {
    $('#publications_overview').DataTable( {
      "paging": true,
      "pageLength":20,
      "searching": true
    } );
  });
