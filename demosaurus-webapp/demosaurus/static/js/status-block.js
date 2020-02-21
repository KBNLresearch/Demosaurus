

  function init(){

    for(var i = 0; i< contributors.length; i++){
            add_status_row(name=contributors[i].name);
  }
  }

  function add_status_row(name="") {
    $("#statustable > tbody").append($('<tr>')
      .append($('<td>').append('<input onclick="move_row(this,1);" type="button" value="&#8679;">'))
      .append($('<td>').append('<input onclick="move_row(this,0);" type="button" value="&#8681;">'))
      .append($('<td>').append('<input id="aut_name_' + maxIndex + '" type="text" placeholder="Voornaam @Achternaam" value="'+ name+'">'))
      .append($('<td>').append('<input class="role" id="role_' + maxIndex + '">'))
      .append($('<td>').append('<input onclick="thesaureer('+maxIndex+');" type="button" value="Zoek in NTA" id="thesaureerButton_'+maxIndex+'">'))
      )
    $('input[id="role_' + maxIndex + '"]').autocomplete({
      source: role_options
    });
    maxIndex ++;
  }

  function thesaureer(index){
    var authornameId = "aut_name_" + index;
    var authorname = $("#"+ authornameId).val();
    console.log('Thesaureer name', authorname)

    $('#thesaureer_title').text('NTA-records voor '+authorname);

    $.ajax({
      url: '/thesaureer_2',
      data: {'author_name': authorname},
      dataType: 'json',
      success:  thesaureer_response,
        error: function(error) {
          console.log(error);
        }
      });
  }
