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
      .append($('<td class="score_cell">').append($('<div>').css("backgroundColor",getColorForPercentage(row.score))
        .text(Math.round(100*row.score))))
      .append($('<td class="score_cell">').append($('<div>').css("backgroundColor",getColorForPercentage(row.name_score,row.name_confidence))
        .text(Math.round(100*row.name_score))))
      .append($('<td class="score_cell">').append($('<div>').css("backgroundColor",getColorForPercentage(row.style_score, row.style_confidence))
        .text(Math.round(100*row.style_score))))
      .append($('<td class="score_cell">').append($('<div>').css("backgroundColor",getColorForPercentage(row.genre_score,row.genre_confidence))
        .text(Math.round(100*row.genre_score))))
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
                .append($('<th scope="col" class="score_cell">').append($('<div>').append($('<span>').text('Totaal'))))
                .append($('<th scope="col" class="score_cell">').append($('<div>').append($('<span>').text('Naam'))))
                .append($('<th scope="col" class="score_cell">').append($('<div>').append($('<span>').text('Stijl'))))
                .append($('<th scope="col" class="score_cell">').append($('<div>').append($('<span>').text('Genre')))));
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