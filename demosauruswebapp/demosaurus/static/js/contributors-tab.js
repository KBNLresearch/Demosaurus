var focus_index;
var main_author = true;

$(document).ready(function() {

  //if (pilotMode) {
  if (false){
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
    .append($('<td class="name_cell">').append('<input class="aut_name" id="aut_name_' + maxIndex + '" type="text" placeholder="Voornaam @Achternaam" value="'+ name+'">'))
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
  $(".aut_name").css("backgroundColor","");
  $(".ppn").css("backgroundColor","");
  $(".role").css("backgroundColor","");    
}
  // Hover over Match column shows scores.
  $(function() {
      $('#authorMatchTt').tooltip({ content: $('#authorMatchHover').html() });
  });

  $(function() {
      $('#thesMatchTt').tooltip({ content: $('#thesMatchHover').html() });
  });

function thesaureer(index){
  console.log(genres)

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

function candidate_note(candidaterow){
  return ''
    +(candidaterow.skopenote_nl || '')+' '
    +(candidaterow.editorial || '')+' '
    +(candidaterow.editorial_nl || '')+' '
}


  function thesaureer_response(response, contributor_row) {
        // console.log(response);
        // console.log(contributor_row);
        $("body").css("cursor", "default");

        if (response.length<1) {
          $('#placeholder').text('Geen records gevonden');
          //$("#candidate_list > thead").empty()
          if ( $.fn.dataTable.isDataTable('#candidate_list') ) {
            $('#candidate_list').DataTable().destroy();
            $('#candidate_list tr').remove();
            $('#candidate_list th').remove();
          }

        }
        else {

          // Destroy datatable if exists, reset #candidate_list table.
          if ( $.fn.dataTable.isDataTable('#candidate_list') ) {
            $('#candidate_list').DataTable().destroy();
            $('#candidate_list tr').remove();
            $('#candidate_list th').remove();
          }

          $('#placeholder').empty()
          if ($("#candidate_list > thead > tr").length<1){
              $("#candidate_list > thead").append($('<tr>')
                .append($('<th scope="col" padding="0px">').html(""))
                .append($('<th scope="col" class="ppn_cell">').text('PPN'))
                .append($('<th scope="col" class="name_cell">').text('Naam'))
                .append($('<th scope="col">').text('ISNI'))
                .append($('<th scope="col" class="name_cell">').text('Notitie'))
                .append($('<th scope="col" class="years_cell">').text('Leefjaren'))
                .append($('<th scope="col" class="match_cell">').text('Match'))
              );
            }

          // Determine context for display on contributor page
          try {var role = $('#role_'+contributor_row).val().match(/\[(.*?)\]/)[1];}
          catch(e) {var role = null; }
          var context = {'Title':$('#publication_title').val(), 'Role':role};

          for(var i = 0; i<response.length; i++){
            //add_to_candidate_list(response[i], context);
            console.log('add_to_candidate_list now')
            console.log(response[i])
              var years = [response[i].birthyear,'-',response[i].deathyear].join('');
              context['id']=response[i].author_ppn;
              color = getColorForPercentage(response[i].score);

              $("#candidate_list > tbody").append($('<tr onclick="choose_ppn(\''+response[i].author_ppn+'\')"; return false;>')
                .append($('<td>').append('<input onclick="delete_row(this);" type="button" value="&#xf2ed;" class="fas fa-trash-alt" title="Verwijder naam" padding="0px">'))
                .append($('<td class="ppn_cell" >').text(response[i].author_ppn))
                .append($('<td class="name_cell">')
                  .append($('<a class="action"  title="Details" href="#" onClick="open_popup(\''+Flask.url_for('contributor.authorpage', context)+'\')"; return false;>')
                    .text(response[i].foaf_name)))
                .append($('<td>').html((response[i].isni?'&#10003;':'')))
                .append($('<td class="name_cell" title="'+candidate_note(response[i])+'">').text(candidate_note(response[i])).tooltip())
                .append($('<td class="years_cell">')
                  .text(years))
                .append($('<td class="match_cell" data-rij="' + i + '" id="thesMatchTt" style="background-color:'+color+'">').text(Math.round(100*response[i].score)))
                )


                //        .append($('<td onclick="addSubjectRow(\''+category+'\',\''+ term+'\',\''+ identifier+'\')" title="Selecteer term">').text(term))

            };
          // Hover div on Match with sub-scores.
          $('.match_cell').hover(
          function() {



            var tooltipValues = [];
            //$('#tttb2').text(Math.round(response[$(this).data("rij")]["role_score"]*100) + '%');
            //$('#tttb3').text(Math.round(response[$(this).data("rij")]["role_confidence"]*100) + '%');

            $('#tttb5').text(Math.round(response[$(this).data("rij")]["genre_score"]*100) + '%');
            $('#tttb6').text(Math.round(response[$(this).data("rij")]["genre_confidence"]*100) + '%');

            $('#tttb14').text(Math.round(response[$(this).data("rij")]["name_score"]*100) + '%');
            $('#tttb15').text(Math.round(response[$(this).data("rij")]["name_confidence"]*100) + '%');

            $('#tttb8').text(Math.round(response[$(this).data("rij")]["jvu_score"]*100) + '%');
            $('#tttb9').text(Math.round(response[$(this).data("rij")]["jvu_confidence"]*100) + '%');


            var tooltip = $("<div class='tooltip'>" + $('#thesMatchHover').html() + "</div>")
              .css({
                'color': '#363838',
                'position': 'absolute',
                'zIndex': '99999',
                'width': '200px',
                'right':'150px',
                'height': '150px',
                'background-color': 'rgba(34, 204, 240, 0)',
              });
            $(this).append(tooltip);
//            $(document).on('mousemove', function(e) {
//              $('.tooltip').css({
//                // pageX, pageY need to relocate (ie subtract 325 and 635) because DataTabels.js does somethin weird.
//                left: e.pageX - 325,
//                top: e.pageY - 475
//              });
//            });
          },
          function() {
            $('.tooltip').remove();
            }
          );


          $('#candidate_list').DataTable({ordering: false});

          $('#candidate_list').on('click', '.fas.fa-trash-alt', function(){
            var cl = $('#candidate_list').DataTable();
            cl
              .row($(this).parents('tr'))
              .remove()
              .draw();
          });
        }
    };

function choose_ppn(ppn) {
  console.log('Choose', ppn);
  $('#ppn_'+focus_index).val(ppn);
}
