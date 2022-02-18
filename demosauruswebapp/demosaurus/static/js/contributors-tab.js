var candidates;
var focus_index;
var main_author = true;


$(document).ready(function() {
  $("#candidate_list").hide();
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
    .append($('<td>').append('<input onclick="search_for_candidates('+maxIndex+');" type="button" value="&#xf002" class="fas fa-search" title="Thesaureer naam" id="thesaureerButton_'+maxIndex+'">'))
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

function candidate_note(candidaterow){
  return ''
    +(candidaterow.skopenote_nl || '')+' '
    +(candidaterow.editorial || '')+' '
    +(candidaterow.editorial_nl || '')+' '
}

function search_for_candidates(index){
  $("#candidate_list").show();
  if ( $.fn.dataTable.isDataTable('#candidate_list') ) {
      $('#candidate_list').DataTable().destroy();
    }
  activate_row(index);
  try {var role = $('#role_'+index).val().match(/\[(.*?)\]/)[1];}
  catch(e) {var role = null; }

  var contributor_name =  $("#aut_name_" + index).val();
  var data = {
           'contributor_name' : contributor_name,
           'contributor_role' : role,
           'publication_title': $('#publication_title').text(),
           'publication_genres': JSON.stringify(genres),
           'publication_year': $('#publicationYear').text(),
           'extended_search': false
         };

  console.log('Thesaureer');

  console.log(data);
    candidates = $("#candidate_list").DataTable( {
      ajax: {
        "url": '/thesaureer',
        "data": data,
        "dataType": 'json',
        "dataSrc": ''
      },
      columns: [
        { "data": null, className: "dt-center editor-delete", defaultContent: '<i class="fa fa-trash"/>', orderable: false},
        { "data" : "author_ppn", className: "pick-author highlight", tooltip: "<span class='name_column_tip'>Kies auteur</span>"
        },
        { "data" : "foaf_name"
          , render: function( data, type, row ){
            try {var role = $('#role_'+index).val().match(/\[(.*?)\]/)[1];}
              catch(e) {var role = null; }
              var context = {'id':row.author_ppn, 'Title':$('#publication_title').textContent, 'Role':role};
              return '<a class="action"  title="Details" href="#" onClick="open_popup(\''+Flask.url_for('contributor.authorpage', context)+'\')"; return false;>'+row.foaf_name+'</a>';
        }
        },
        { "data" : "isni", render: function( data, type, row ){
          return row.isni?'X':'-';
        }},
        { "data" : "note", render: function( data, type, row ){
          //$.fn.dataTable.render.ellipsis( 17, true )
          return candidate_note(row);
        }},
        { "data" : "Leefjaren", render: function( data, type, row ){
          return (row.birthyear|| '') +'-'+(row.deathyear|| '');
        }},
        { "data" : "score", render: function ( data, type, row ) {
          var score_show = (row.score===null || typeof(row.score)==='undefined')?'':Math.round(100*row.score)+'%';
          var score_hover = '<div title="Alle subscores"</div>' // I have no clue why deleting this bit renders the tooltip created in rowCallback useless..
          return type === 'display'? score_hover + score_show : score_show;
        }, className: "match_cell"},
      ],
       "rowCallback": function( row, data, index ) {
         if (! isNaN(data.score)) {
            $('td.match_cell', row).css('background-color', getColorForPercentage(data.score));
         }
         var score_hover = '<div><table><tbody>'
         var scores_to_show = [['Genre',data.genre_score,data.genre_confidence], ['Rol',data.role_score,data.role_confidence],['Jaar',data.year_score,data.year_confidence]];

         for (var i=0; i < scores_to_show.length; i++) {
           console.log(scores_to_show[i])
           scorename = scores_to_show[i][0]
           subscore = scores_to_show[i][1]
           scorestring = subscore===null?subscore:Math.round(100*subscore)+'%'
           subconfidence = scores_to_show[i][2]
           confidencestring = (subconfidence===null || typeof(subconfidence)==='undefined')?'':'('+Math.round(100*subconfidence)+'% zeker)'
           score_hover += '<tr><th>'+scorename+'</th><td style="text-align:right">'+scorestring+'</td><td style="text-align:right">'+confidencestring+'</td></tr>'
         }
         score_hover += '</tbody></table></div>'
        $('td.match_cell', row).tooltip({content: score_hover})
        }
    });
  }

$('#candidate_list').on('click', 'td.editor-delete', function () {
        candidates
          .row( $(this).parents('tr') )
          .remove()
          .draw();
    } );

$('#candidate_list').on('click', 'td.pick-author', function () {
   $('#ppn_'+focus_index).val($(this).text());
    } );