function score_span(score,confidence){
  hovertext = "".concat('Score: ',String(Math.round(100*score)), '&#37; Confidence: ', String(Math.round(100*confidence)),'&#37;');
  return $('<span title="'+hovertext+'" data-html="true" style="display: inline-block; width: 30px; height: 15px">')
        .css("backgroundColor",getColorForPercentage(score,confidence))
        .tooltip({})
}

function candidate_note(candidaterow){
  return ''
    +(candidaterow.skopenote_nl || '')+' '
    +(candidaterow.editorial || '')+' '
    +(candidaterow.editorial_nl || '')+' '

}

function add_to_candidate_list(row){
  console.log('add_to_candidate_list now')
    var years = [row.birthyear,'-',row.deathyear].join('');

    $("#candidate_list > tbody").append($('<tr>')
      .append($('<td>').append('<input onclick="delete_row(this);" type="button" value="&#10007;">'))
      .append($('<td class="ppn_cell" >')
        .append($('<a class="action" href="#" onclick="choose_ppn(\''+row.ppn+'\')"; return false;>')
          .text(row.ppn)))
      .append($('<td class="name_cell">')
        .append($('<a class="action"  href="#" onClick="open_popup(\''+Flask.url_for('contributor.authorpage', {'id':row.ppn})+'\')"; return false;>')
          .text(row.foaf_name)))
      .append($('<td class="name_cell">').text(candidate_note(row)))
      .append($('<td class="years_cell">')
        .text(years))
      .append($('<td class="years_cell">').append($('<div>').css("backgroundColor",getColorForPercentage(row.score))
        .text(Math.round(100*row.score))))
      .append($('<td class="score_cell">').append(score_span(row.name_score,row.name_confidence)))
      .append($('<td class="score_cell">').append(score_span(row.role_score,row.role_confidence)))
      .append($('<td class="score_cell">').append(score_span(row.genre_score,row.genre_confidence)))
      .append($('<td class="score_cell">').append(score_span(row.topic_score,row.topic_confidence)))
      .append($('<td class="score_cell">').append(score_span(row.style_score, row.style_confidence)))
      );
  }


  function thesaureer_response(response) {
        console.log(response);

        if (response.length<1) {
          $('#placeholder').text('Geen records gevonden');
          $("#candidate_list > thead").empty()
        }
        else {
          $('#placeholder').empty()
          if ($("#candidate_list > thead > tr").length<1){
              $("#candidate_list > thead").append($('<tr>')
                .append($('<th scope="col">').html("&#10007;"))
                .append($('<th scope="col" class="ppn_cell">').text('PPN'))
                .append($('<th scope="col" class="name_cell">').text('Naam'))
                .append($('<th scope="col" class="name_cell">').text('Notitie'))
                .append($('<th scope="col" class="years_cell">').text('Leefjaren'))
                .append($('<th scope="col" class="match_cell">').text('Match'))
                .append($('<th scope="col" class="score_cell">').append($('<div>').append($('<span>').text('Naam'))))
                .append($('<th scope="col" class="score_cell">').append($('<div>').append($('<span>').text('Rol'))))
                .append($('<th scope="col" class="score_cell">').append($('<div>').append($('<span>').text('Genre'))))
                .append($('<th scope="col" class="score_cell">').append($('<div>').append($('<span>').text('Onderwerp'))))
                .append($('<th scope="col" class="score_cell">').append($('<div>').append($('<span>').text('Stijl'))))
                );
            }
          }

          ndisplay = Math.min(response.length, 20);
          // Figure out how to deal with pagination.. 
          console.log('Display:', ndisplay);

          for(var i = 0; i< ndisplay; i++){
            console.log(i);
            add_to_candidate_list(response[i]);
          }

        }

function choose_ppn(ppn) {
  console.log('Choose', ppn);
  $('#ppn_'+focus_index).val(ppn); 
}