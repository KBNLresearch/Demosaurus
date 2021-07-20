var focus_index;
var main_author = true;

function init(){
  document.getElementById("contributors_tab").click();
  if (contributors.length < 1){
    add_contributor_row();
  }
  for(var i = 0; i< contributors.length; i++){
    console.log(contributors[i]);
    add_contributor_row(name=contributors[i].name, role=contributors[i].role);
  }
  top_main_author();
}

function add_contributor_row(name="", role="") {
  $("#contributortable > tbody").append($('<tr id="row_' + maxIndex+'">')
    .append($('<td>').append('<input onclick="delete_row(this);" type="button" value="&#xf2ed" class="fas fa-trash-alt" title="Verwijder naam">'))
    .append($('<td>').append('<input onclick="move_row(this,1); top_main_author();" type="button" value="&#xf062" class="fas fa-arrow-up" title="Verplaats omhoog">'))
    .append($('<td>').append('<input onclick="move_row(this,0); top_main_author();" type="button" value="&#xf063" class="fas fa-arrow-down" title="Verplaats omlaag">'))
    .append($('<td class="name_cell">').append('<input id="aut_name_' + maxIndex + '" type="text" placeholder="Voornaam @Achternaam" value="'+ name+'">'))
    .append($('<td class="name_cell">').append('<input type="text" class="role" id="role_' + maxIndex + '" value="'+ (role? '['+role+']' :'' )+ '">'))
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
  var contributorname = $("#aut_name_" + index).val();
  try {var role = $('#role_'+index).val().match(/\[(.*?)\]/)[1];}
  catch(e) {var role = null; }

  activate_row(index);

  $("#candidate_list > tbody").empty()
  $('#thesaureer_title').text('NTA-records voor '+contributorname);

  $.ajax({
    url: '/thesaureer',
    data: {'contributor_name' : contributorname,
          'contributor_role' : role,
           'publication_title': $('#publication_title').val(),
           'publication_genres': JSON.stringify(genres)
         },
    dataType: 'json',
    context:this,
    success: function(response){
      thesaureer_response(response,index);
    },
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

  var contributors = []; 
  var all_kmcs = '';

  // build up kmc contents for contributors: contributorname$role$!ppn!viafname
  var rows = $('#contributortable > tbody > tr');
  var at_kmc = 3011;
  for (var i=0; i < rows.length; i++) {
    var id = rows[i].id.split('_')[1];
    console.log('row', id);

    console.log($('#main_'+id).is(':checked'));



    if (i==0 && $('#main_'+id).is(':checked')){
      all_kmcs += '<p>3000\t';
    }
    else {
      all_kmcs += "<p>"+at_kmc+"\t";
      if (at_kmc <3019) {
        at_kmc ++;
      }
    }

    all_kmcs += $('#aut_name_'+id).val();
    role = $('#role_'+id).val();
    if (role) { 
        role = role.replace(/(^.*\[|\].*$)/g, ''); // get the role-code bit
        all_kmcs += '$'+ role +'$';
      }
      else {
        $('#role_'+id).css("backgroundColor","red");
        allroles = false; 
      }

      ppn = $('#ppn_'+id).val();
      if (ppn) {
        all_kmcs += '!'+ ppn +'!';
      }
      else {
        $('#ppn_'+id).css("backgroundColor","red");
        allppns = false; 
      }
      all_kmcs += "</p>";
    }
    
    $('#contributors_tab_flag').css("visibility","hidden");

    // Report about the completeness of the input
    if (! allroles) {
        $('#contributors_tab_flag').css("visibility","visible");
        $('#export > #message').append('<br><i>&#8226; Let op: niet bij alle auteurs is de rol ingevoerd!</i></br>');
      }
    if (! allppns) {
        $('#contributors_tab_flag').css("visibility","visible");
        $('#export > #message').append('<br><i>&#8226; Let op: niet alle auteurs zijn gethesaureerd!</i></br>');
      }

      $('#thesaureer_title').text('KMCS:');
      //$("#candidate_list > thead").empty();    
      //$("#candidate_list > tbody").empty();

    
    // Serve collected information in the web application
    // NB todo: export primary author (if they exist) to KMC 3000 rather than 3011
    $('#export_content').html(all_kmcs);
  }

  /*
  function suggest_topics() {
    console.log('Annif button clicked')
    $("#candidate_lis").empty();    
    $('#placeholder').html('Annif API not connected');
  }
  */