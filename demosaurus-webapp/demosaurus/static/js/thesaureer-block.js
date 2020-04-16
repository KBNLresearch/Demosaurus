function score_span(score,confidence){
  hovertext = "".concat('Score: ',String(Math.round(100*score)), '&#37; Confidence: ', String(Math.round(100*confidence)),'&#37;');
  return $('<span title="'+hovertext+'" data-html="true" style="display: inline-block; width: 30px; height: 15px">')
        .css("backgroundColor",getColorForPercentage(score,confidence))
        .tooltip({})
}


function add_to_author_list(row){


    var years = [row.birthyear,'-',row.deathyear].join('');

    $("#author_list > tbody").append($('<tr>')
      .append($('<td class="ppn_cell" >')
        .append($('<a class="action" href="#" onclick="choose_ppn(\''+row.ppn+'\')"; return false;>')
          .text(row.ppn)))
      .append($('<td class="name_cell">')
        .append($('<a class="action"  href="#" onClick="open_popup(\''+Flask.url_for('contributor.authorpage', {'id':row.ppn})+'\')"; return false;>')
          .text(row.foaf_name)))
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
          $("#author_list > thead").empty()
        }
        else {
          $('#placeholder').empty()
          if ($("#author_list > thead > tr").length<1){
              $("#author_list > thead").append($('<tr>')
                .append($('<th scope="col" class="ppn_cell">').text('PPN'))
                .append($('<th scope="col" class="name_cell">').text('Naam'))
                .append($('<th scope="col" class="years_cell">').text('Leefjaren'))
                .append($('<th scope="col" class="years_cell">').text('Match'))
                .append($('<th scope="col" class="score_cell">').append($('<div>').append($('<span>').text('Naam'))))
                .append($('<th scope="col" class="score_cell">').append($('<div>').append($('<span>').text('Rol'))))
                .append($('<th scope="col" class="score_cell">').append($('<div>').append($('<span>').text('Genre'))))
                .append($('<th scope="col" class="score_cell">').append($('<div>').append($('<span>').text('Onderwerp'))))
                .append($('<th scope="col" class="score_cell">').append($('<div>').append($('<span>').text('Stijl'))))
                );
            }
          }

          $("#author_list > tbody").empty()
          for(var i = 0; i< response.length; i++){
            add_to_author_list(response[i]);
          }

        }

function choose_ppn(ppn) {
  console.log('Choose', ppn);
  $('#ppn_'+focus_index).val(ppn); 
}