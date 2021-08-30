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

  console.log('Open tab', tabName)

  var i, tabcontent, tablinks;

  // Get all elements with class="tabcontent" and hide them
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  document.getElementById(tabName).style.display = "block";
  
  // When switching tabs, also show the corresponding results (2nd half of page).
  // FIX: doesn't show back after hiding, .style.display = "block"; ?
  bottomcontent = document.getElementsByClassName("bottomcontent");
  for (i = 0; i < bottomcontent.length; i++) {
    bottomcontent[i].style.display = "none";
  }

  // Get all elements with class="tablinks" and remove the class "active"
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }

  // Show the current tab, and add an "active" class to the button that opened the tab
  document.getElementById(tabName + "_content").style.display = "block";
  evt.currentTarget.className += " active";

}

/*
function score_span(score,confidence){
  hovertext = "".concat('Score: ',String(Math.round(100*score)), '&#37; Confidence: ', String(Math.round(100*confidence)),'&#37;');
  return $('<div title="'+hovertext+'" data-html="true">')
        .css("background-color",getColorForPercentage(score))
        .css("width",Math.round(50*confidence))
        .tooltip({})
}
*/

var getColorForPercentage = function(this_perc, saturation=1.0, low=0.5) {
    var percentColors = [
    { pct: 0.0, color: { r: 0xff, g: 0x00, b: 0 } },
    { pct: low, color: { r: 0xff, g: 0xff, b: 0 } },
    { pct: 1.0, color: { r: 0x00, g: 0xff, b: 0 } } ];

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
  
  // Hover over Match column shows scores.
  $(function() {
      $('#authorMatchTt').tooltip({ content: $('#authorMatchHover').html() });
  });

  $(function() {
      $('#thesMatchTt').tooltip({ content: $('#thesMatchHover').html() });
  });

  // DataTabel.js init interactive tables.
  $(document).ready( function () {
    $('#publication_list').DataTable();
    var ann_results = $('#annif-results-table').DataTable( {
      paging: false,
      searching: false,
      info: false,
      columnDefs: [
        {width: 500, targets: 0 }
      ],
      fixedColumns: true,
      select: true
    } );
    $('#annif-results-table').parents('div.dataTables_wrapper').first().hide();
} );
