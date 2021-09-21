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