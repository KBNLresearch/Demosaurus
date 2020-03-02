function add_to_author_list(row){

    var url = "{{ url_for('contributor.authorpage', id='placeholder')}}".replace('placeholder', row.ppn);

    console.log(url);

    var link = '<a class="action"  href="#" onClick="open_popup(\''+url+'\')"; return false;>'+row.foaf_name+'</a>';
    console.log('link',link);


    var choose = $('<a class="action" href="#" onclick="choose_ppn(\'placeholder\')"; return false;>'.replace('placeholder', row.ppn));

    var years = [row.birthyear,'-',row.deathyear].join('');

    $("#author_list > tbody").append($('<tr>')
      .append($('<td class="ppn_cell" >').append(choose.text(row.ppn)))
      .append($('<td class="name_cell">').append(link))
      .append($('<td class="years_cell">').text(years))
      .append($('<td class="score_cell">').css("backgroundColor",getColorForPercentage(row.name_score)).text(Math.round(row.name_score)))
      );
  }


  var getColorForPercentage = function(this_perc, low=0.5) {
    var percentColors = [
    { pct: 0.0, color: { r: 0xff, g: 0x00, b: 0 } },
    { pct: low, color: { r: 0xff, g: 0xff, b: 0 } },
    { pct: 1.0, color: { r: 0x00, g: 0xff, b: 0 } } ];

    this_perc = Number(this_perc) / 100;
    for (var i = 1; i < percentColors.length - 1; i++) {
      if (this_perc < percentColors[i].pct) {
        break;
      }
    }
    var lower = percentColors[i - 1];
    var upper = percentColors[i];
    var range = upper.pct - lower.pct;
    var rangePct = (this_perc - lower.pct) / range;
    var pctLower = 1 - rangePct;
    var pctUpper = rangePct;
    var color = {
      r: Math.floor(lower.color.r * pctLower + upper.color.r * pctUpper),
      g: Math.floor(lower.color.g * pctLower + upper.color.g * pctUpper),
      b: Math.floor(lower.color.b * pctLower + upper.color.b * pctUpper)
    };
    return 'rgb(' + [color.r, color.g, color.b].join(',') + ')';
  };

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
                .append($('<th scope="col" class="name_cell">').text('Name'))
                .append($('<th scope="col" class="years_cell">').text('Leefjaren'))
                .append($('<th scope="col" class="score_cell">').append($('<div>').text('Name'))));
            }
          }

          $("#author_list > tbody").empty()
          for(var i = 0; i< response.length; i++){
            add_to_author_list(response[i]);
          }

        }

function choose_ppn(ppn) {
  console.log('choose this!',ppn)

  console.log('into', $('#ppn_'+focus_index))
  $('#ppn_'+focus_index).val(ppn); 

}