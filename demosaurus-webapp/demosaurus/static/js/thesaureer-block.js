function candidate_note(candidaterow){
  return ''
    +(candidaterow.skopenote_nl || '')+' '
    +(candidaterow.editorial || '')+' '
    +(candidaterow.editorial_nl || '')+' '
}


  function thesaureer_response(response, contributor_row) {
        // console.log(response);
        // console.log(contributor_row);

        if (response.length<1) {
          $('#placeholder').text('Geen records gevonden');
          $("#candidate_list > thead").empty()
          if (cl != null) {cl.destroy();}

        }
        else {
          $('#placeholder').empty()
          if ($("#candidate_list > thead > tr").length<1){
              $("#candidate_list > thead").append($('<tr>')
                .append($('<th scope="col" padding="0px">').html("&#10007;"))
                .append($('<th scope="col" class="ppn_cell">').text('PPN'))
                .append($('<th scope="col" class="name_cell">').text('Naam'))
                .append($('<th scope="col">').text('ISNI'))
                .append($('<th scope="col" class="name_cell">').text('Notitie'))
                .append($('<th scope="col" class="years_cell">').text('Leefjaren'))
                .append($('<th scope="col" class="match_cell">').text('Match'))
              );
            }
            
          console.log('Creating context for publication');
          try {var role = $('#role_'+contributor_row).val().match(/\[(.*?)\]/)[1];}
          catch(e) {var role = null; }
          console.log('Role:', role)
          
          var context = {'Title':$('#publication_title').val(), 'Role':role};
          console.log('Context is nu:', context);

          for(var i = 0; i<response.length; i++){
            //add_to_candidate_list(response[i], context);
            console.log('add_to_candidate_list now')
            console.log(response[i])
              var years = [response[i].birthyear,'-',response[i].deathyear].join('');
              context['id']=response[i].author_ppn;

              $("#candidate_list > tbody").append($('<tr>')
                .append($('<td>').append('<input onclick="delete_row(this);" type="button" value="&#10007;" padding="0px">'))
                .append($('<td class="ppn_cell" >')
                  .append($('<a class="action" href="#" onclick="choose_ppn(\''+response[i].author_ppn+'\')"; return false;>')
                    .text(response[i].author_ppn)))
                .append($('<td class="name_cell">')
                  .append($('<a class="action"  href="#" onClick="open_popup(\''+Flask.url_for('contributor.authorpage', context)+'\')"; return false;>')
                    .text(response[i].foaf_name)))
                .append($('<td>').html((response[i].isni?'&#10003;':'')))
                .append($('<td class="name_cell" title="'+candidate_note(response[i])+'">').text(candidate_note(response[i])).tooltip())
                .append($('<td class="years_cell">')
                  .text(years))
                .append($('<td class="match_cell" data-rij="' + i + '" id="thesMatchTt">').append($('<div>').css("background-color",getColorForPercentage(response[i].score))
                  .text(Math.round(100*response[i].score))))
                )
            };
          // Hover div on Match with sub-scores. 
          $('.match_cell').hover(
          function() {
            var tooltipValues = [];
            $('#tttb2').text(Math.round(response[$(this).data("rij")]["role_score"]*100) + '%');
            $('#tttb3').text(Math.round(response[$(this).data("rij")]["role_confidence"]*100) + '%');
            
            $('#tttb5').text(Math.round(response[$(this).data("rij")]["genre_score"]*100) + '%');
            $('#tttb6').text(Math.round(response[$(this).data("rij")]["genre_confidence"]*100) + '%');
            
            $('#tttb8').text(Math.round(response[$(this).data("rij")]["topic_score"]*100) + '%');
            $('#tttb9').text(Math.round(response[$(this).data("rij")]["topic_confidence"]*100) + '%');

            $('#tttb11').text(Math.round(response[$(this).data("rij")]["style_score"]*100) + '%');
            $('#tttb12').text(Math.round(response[$(this).data("rij")]["style_confidence"]*100) + '%');

            $('#tttb14').text(Math.round(response[$(this).data("rij")]["name_score"]*100) + '%');
            $('#tttb15').text(Math.round(response[$(this).data("rij")]["name_confidence"]*100) + '%');

            var tooltip = $("<div class='tooltip'>" + $('#thesMatchHover').html() + "</div>")
              .css({
                'color': '#363838',
                'position': 'absolute',
                'zIndex': '99999',
                'width': '200px',
                'height': '150px',
                'background-color': 'rgba(34, 204, 240, 0)',
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

          var cl = $('#candidate_list').DataTable();
          }
    };

function choose_ppn(ppn) {
  console.log('Choose', ppn);
  $('#ppn_'+focus_index).val(ppn); 
}