// Create HTML table on authorpage.html

function add_to_publication_list(publications){
  //console.log('add_to_publication_list now')

  $("#publication_list > thead").append($('<tr>')
                .append($('<th scope="col">').html("&#10007;"))
                .append($('<th scope="col" class="ppn_cell">').text('PPN'))
                .append($('<th scope="col" class="title_cell">').text('Naam'))
                .append($('<th scope="col" class="match_cell">').text('Overeenkomst'))
                );

  for(var i = 0; i< publications.length; i++){
            //console.log(i);
            var row = publications[i];
            console.log('add publication', row);

    $("#publication_list > tbody").append($('<tr>')
      .append($('<td>').append('<input onclick="delete_row(this);" type="button" value="&#10007;" padding="0px">'))
      .append($('<td class="ppn_cell" >').text(row.publication_ppn))
      .append($('<td class="title_cell" >').text(row.titelvermelding))
      //.append($('<td class="match_cell">').append($('<div>')
      .append($('<td class="match_cell" data-rij="' + i + '" id="authorMatchTt">').append($('<div>')
          .css("background-color",getColorForPercentage(1))
          .text(Math.round(100*1.))))
      );
  }
  
  // Hover mouse over 'Match' score popups tooltip with table with sub-scores.
  $('.match_cell').hover(
    function() {
      //console.log(publications[$(this).data("rij")])
      var tooltipJSON = publications[$(this).data("rij")];
      var tooltipValues = [];
      $('#tttb2').text(Math.round(publications[$(this).data("rij")]["role_score"]*100) + '%');
      $('#tttb3').text(Math.round(publications[$(this).data("rij")]["role_confidence"]*100) + '%');
      
      $('#tttb5').text(Math.round(publications[$(this).data("rij")]["genre_score"]*100) + '%');
      $('#tttb6').text(Math.round(publications[$(this).data("rij")]["genre_confidence"]*100) + '%');
      
      $('#tttb8').text(Math.round(publications[$(this).data("rij")]["topic_score"]*100) + '%');
      $('#tttb9').text(Math.round(publications[$(this).data("rij")]["topic_confidence"]*100) + '%');

      $('#tttb11').text(Math.round(publications[$(this).data("rij")]["style_score"]*100) + '%');
      $('#tttb12').text(Math.round(publications[$(this).data("rij")]["style_confidence"]*100) + '%');

      //console.log( 'hovering on' , publications[$(this).data("rij")]);
      var tooltip = $("<div class='tooltip'>" + $('#authorMatchHover').html() + "</div>")
        .css({
          'color': '#fff',
          'position': 'absolute',
          'zIndex': '99999',
          'width': '200px',
          'height': '150px',
          'background-color': 'rgba(255, 99, 132, 0)',
        });
      $(this).append(tooltip);
      $(document).on('mousemove', function(e) {
        $('.tooltip').css({
          // pageX, pageY need to relocate (ie subtract 325 and 635) because DataTabels.js does somethin weird.
          left: e.pageX - 325,
          top: e.pageY - 635
        });
      });
  },
  function() {
    $('.tooltip').remove();
  }
  );
}
