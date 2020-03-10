var focus_index;

  function init(){

    for(var i = 0; i< contributors.length; i++){
            add_status_row(name=contributors[i].name);
  }
  }

  function add_status_row(name="") {
    $("#statustable > tbody").append($('<tr id="row_' + maxIndex+'">')
      .append($('<td>').append('<input onclick="move_row(this,1);" type="button" value="&#8679;">'))
      .append($('<td>').append('<input onclick="move_row(this,0);" type="button" value="&#8681;">'))
      .append($('<td>').append('<input id="aut_name_' + maxIndex + '" type="text" placeholder="Voornaam @Achternaam" value="'+ name+'">'))
      .append($('<td>').append('<input class="role" id="role_' + maxIndex + '">'))
      .append($('<td>').append('<input class="ppn" id="ppn_' + maxIndex + '">'))
      .append($('<td>').append('<input onclick="thesaureer('+maxIndex+');" type="button" value="Zoek in NTA" id="thesaureerButton_'+maxIndex+'">'))
      )
    $('input[id="role_' + maxIndex + '"]').autocomplete({
      source: role_options
    });
    maxIndex ++;
  }

  function activate_row(index) {
    focus_index = index;

    $("#statustable > tbody > tr").css("backgroundColor","");
    $(".ppn").css("backgroundColor","");

    $('#ppn_'+index).css("backgroundColor","red");
    $('#row_'+index).css("backgroundColor","red");

  }

  function thesaureer(index){
    var authornameId = "aut_name_" + index;
    var authorname = $("#"+ authornameId).val();
    console.log('Thesaureer name', authorname);

    activate_row(index);

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

  function export_info() {
    console.log('Export button')

  }

  function suggest_topics() {
    console.log('Annif button')

  }