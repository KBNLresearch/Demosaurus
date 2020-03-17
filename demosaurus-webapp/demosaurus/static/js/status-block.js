var focus_index;

function init(){

  document.getElementById("contributors_tab").click();

  for(var i = 0; i< contributors.length; i++){
    add_status_row(name=contributors[i].name);
  }
}

function add_status_row(name="") {
  $("#statustable > tbody").append($('<tr id="row_' + maxIndex+'">')
    .append($('<td>').append('<input onclick="delete_row(this);" type="button" value="&#10007;">'))
    .append($('<td>').append('<input onclick="move_row(this,1);" type="button" value="&#8679;">'))
    .append($('<td>').append('<input onclick="move_row(this,0);" type="button" value="&#8681;">'))
    .append($('<td>').append('<input id="aut_name_' + maxIndex + '" type="text" placeholder="Voornaam @Achternaam" value="'+ name+'">'))
    .append($('<td>').append('<input class="role" id="role_' + maxIndex + '">'))
    .append($('<td>').append('<input type="checkbox" value="Primair" checked>'))
    .append($('<td>').append('<input class="ppn" id="ppn_' + maxIndex + '">'))
    .append($('<td>').append('<input onclick="thesaureer('+maxIndex+');" type="button" value="Zoek in NTA" id="thesaureerButton_'+maxIndex+'">'))
    )
  $('input[id="role_' + maxIndex + '"]').autocomplete({
    source: role_options
  });
  maxIndex ++;
}


function activate_row(index) {
  deactivate_rows();
  focus_index = index;

  $('#ppn_'+index).css("backgroundColor","Chartreuse");
  $('#row_'+index).css("backgroundColor","Chartreuse");

}

function deactivate_rows() {
  focus_index = -1;

  $("#statustable > tbody > tr").css("backgroundColor","");
  $(".ppn").css("backgroundColor","");    
  $(".role").css("backgroundColor","");    
}

function thesaureer(index){
  var authornameId = "aut_name_" + index;
  var authorname = $("#"+ authornameId).val();
  console.log('Thesaureer name', authorname);

  activate_row(index);

  $('#thesaureer_title').text('NTA-records voor '+authorname);

  $.ajax({
    url: '/thesaureer_2',
    data: {'author_name': authorname},
    dataType: 'json',
    success:  thesaureer_response,
    error: function(error) {
      console.log(error);
    }
  });
}

function export_info() {
  console.log('Export button')

  deactivate_rows();
  $("#export > #message").empty();

  var allroles = true; 
  var allppns = true; 

  var kmcs = [];

  var rows = $('#statustable > tbody > tr');
  for (var i=0; i < rows.length; i++) {
    var id = rows[i].id.split('_')[1];
    console.log('row', id);
    kmc = '301'+i;
    kmc += '\t'+ $('#aut_name_'+id).val()

    role = $('#role_'+id).val()
    if (role) { 
        role = role.replace(/(^.*\[|\].*$)/g, ''); // get the role-code bit
        kmc += '$'+ role +'$';
      }
      else {
        $('#role_'+id).css("backgroundColor","red");
        allroles = false; 
      }

      ppn = $('#ppn_'+id).val()
      if (ppn) {
        kmc += '!'+ ppn +'!';
      }
      else {
        $('#ppn_'+id).css("backgroundColor","red");
        allppns = false; 
      }

      kmcs.push(kmc)
    }

    console.log('allroles:', allroles, 'allppns:', allppns)
    if (! allroles) {
        //$('#contributors_tab').css("backgroundColor","red");
        $('#export > #message').append('<br>Let op: niet bij alle auteurs is de rol ingevoerd!');
        console.log('message', $('#export > #message'));
      }
      if (! allppns) {
        $('#contributors_tab').css("textColor","red");
        $('#export > #message').append('<br>Let op: niet alle auteurs zijn gethesaureerd!');
      }

      $('#thesaureer_title').text('KMCS:');
      $("#author_list > thead").empty();    
      $("#author_list > tbody").empty();

    $('#placeholder').html("<p>" + kmcs.join("</p><p>") + "</p>");
    console.log(kmcs.join("</p><p>"))
  }

  function suggest_topics() {
    console.log('Annif button clicked')

  }