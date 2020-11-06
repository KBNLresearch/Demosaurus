



function add_to_publication_list(publications){
  console.log('add_to_publication_list now')

  $("#publication_list > thead").append($('<tr>')
                .append($('<th scope="col">').html("&#10007;"))
                .append($('<th scope="col" class="ppn_cell">').text('PPN'))
                .append($('<th scope="col" class="title_cell">').text('Naam'))
                .append($('<th scope="col" class="match_cell">').text('Overeenkomst'))
                .append($('<th scope="col" class="score_cell">').append($('<div>').append($('<span>').text('Rol'))))
                .append($('<th scope="col" class="score_cell">').append($('<div>').append($('<span>').text('Genre'))))
                .append($('<th scope="col" class="score_cell">').append($('<div>').append($('<span>').text('Onderwerp'))))
                .append($('<th scope="col" class="score_cell">').append($('<div>').append($('<span>').text('Stijl'))))
                );

  for(var i = 0; i< publications.length; i++){
            console.log(i);
            var row = publications[i];
            console.log('add publication', row);

    $("#publication_list > tbody").append($('<tr>')
      .append($('<td>').append('<input onclick="delete_row(this);" type="button" value="&#10007;" padding="0px">'))
      .append($('<td class="ppn_cell" >').text(row.publication_ppn))
      .append($('<td class="title_cell" >').text(row.titelvermelding))
      .append($('<td class="match_cell">').append($('<div>').css("background-color",getColorForPercentage(1))
        .text(Math.round(100*1.))))
      .append($('<td class="score_cell">').append(score_span(row.role_score,row.role_confidence)))
      .append($('<td class="score_cell">').append(score_span(row.genre_score,row.genre_confidence)))
      .append($('<td class="score_cell">').append(score_span(row.topic_score,row.topic_confidence)))
      .append($('<td class="score_cell">').append(score_span(row.style_score, row.style_confidence)))

      );
  }
}
  

