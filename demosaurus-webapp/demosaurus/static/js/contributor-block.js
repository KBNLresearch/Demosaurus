var focus_index;
var main_author = true;

$(document).ready(function() {

  if (pilotMode) {
  console.log('in Pilot mode: create first empty row')
  add_contributor_row(); // For pilot: do not pre-fill the authors
  }
  else{
      if (contributors.length < 1){
        add_contributor_row();
      }
      for(var i = 0; i< contributors.length; i++){
        console.log(contributors[i]);
        add_contributor_row(name=contributors[i].name, role=contributors[i].role);
      }
  }
  top_main_author();
});

function add_contributor_row(name="", role="") {
  $("#contributortable > tbody").append($('<tr id="row_' + maxIndex+'">')
    .append($('<td>').append('<input onclick="delete_row(this);" type="button" value="&#xf2ed" class="fas fa-trash-alt" title="Verwijder naam">'))
    .append($('<td>').append('<input onclick="move_row(this,1); top_main_author();" type="button" value="&#xf062" class="fas fa-arrow-up" title="Verplaats omhoog">'))
    .append($('<td>').append('<input onclick="move_row(this,0); top_main_author();" type="button" value="&#xf063" class="fas fa-arrow-down" title="Verplaats omlaag">'))
    .append($('<td class="name_cell">').append('<input id="aut_name_' + maxIndex + '" type="text" placeholder="Voornaam @Achternaam" value="'+ name+'">'))
    .append($('<td class="name_cell">').append('<input type="text" class="role" id="role_' + maxIndex + '" value="'+ (role? '['+role+']' :'' )+ '">')) // pre-fill the role
    //.append($('<td class="name_cell">').append('<input type="text" class="role" id="role_' + maxIndex + '" value="">')) // do not pre-fill the role
    .append($('<td class="name_cell">').append('<input type="text" class="ppn" id="ppn_' + maxIndex + '">'))
    .append($('<td>').append('<input onclick="thesaureer('+maxIndex+');" type="button" value="&#xf002" class="fas fa-search" title="Thesaureer naam" id="thesaureerButton_'+maxIndex+'">'))
    .append($('<td class="check_main_author">').append('<input  type="checkbox" value="Primair" checked id="main_'+maxIndex+'">').append('<span>Hoofdauteur</span>'))
    )
  $('input[id="role_' + maxIndex + '"]').autocomplete({
    source: role_options
  });
  maxIndex ++;
}

function top_main_author(){
  rows = $("#contributortable > tbody").find('tr')
  for (var i=1; i < rows.length; i++) {
    $(rows[i]).find('.check_main_author').css("visibility","hidden");  
  }
  $(rows[0]).find('.check_main_author').css("visibility","visible");  
}

function activate_row(index) {
  deactivate_rows();
  focus_index = index;

  $('#ppn_'+index).css("background-color","#ddd");
  $('#row_'+index).css("background-color","#ccc");

}

function deactivate_rows() {
  focus_index = -1;

  $("#contributortable > tbody > tr").css("backgroundColor","");
  $(".ppn").css("backgroundColor","");    
  $(".role").css("backgroundColor","");    
}

function thesaureer(index){

  var assignedGenres = {'brinkman':[], 'CBK_genre':[]};

  $('#brinkman-table .subjectbox.vorm').each(function(i, elem) {
    assignedGenres['brinkman'].push($(this).text())
  });
  $('#CBK_genre-table .subjectbox ').each(function(i, elem) {
    assignedGenres['CBK_genre'].push($(this).text())
  });

  console.log(genres)
  console.log(assignedGenres)


  $("#candidate_list > tbody").empty()
  activate_row(index);
  $("body").css("cursor", "progress");
  try {var role = $('#role_'+index).val().match(/\[(.*?)\]/)[1];}
  catch(e) {var role = null; }

  var contributor_name =  $("#aut_name_" + index).val();
  var data = {
           'contributor_name' : contributor_name,
           'contributor_role' : role,
           'publication_title': $('#publication_title').text(),
           'publication_genres': JSON.stringify(genres),
           'publication_year': $('#publicationYear').text()
         };

  console.log('Thesaureer');
  console.log(data);

  $.ajax({
    url: '/thesaureer',
    data: data,
    dataType: 'json',
    context:this,
    success: function(response){
      $('#thesaureer_title').text('NTA-records voor '+contributor_name);
      thesaureer_response(response,index);
    },
    error: function(error) {
      console.log(error);
    }
  });
}


