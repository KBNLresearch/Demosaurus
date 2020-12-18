function init_subjects(){
  console.log(subjects)
  for(var i = 0; i< subjects.length; i++){
    console.log(subjects[i]);
    var index = subjects[i].rank;
    if (subjects[i].CBK_genre != "None"){
    //if subjects[i].CBK_genre {}
    $("#table_CBK-genres > tbody").append($('<tr id="subject_row_' + index+'">')
    .append($('<td>').append('<input onclick="delete_row(this);" type="button" value="&#10007;">'))
    .append($('<td>').append('<input onclick="move_row(this,1);" type="button" value="&#8679;">'))
    .append($('<td>').append('<input onclick="move_row(this,0);" type="button" value="&#8681;">'))
    .append($('<td class="name_cell">').append('<input class="cbk_genre" id="cbk_genre_' + index + '" value="'+subjects[i].CBK_genre+ ' ['+subjects[i].CBK_genre_id+']">'))
    )
 	}
    //add_subject_row(name=contributors[i].name, role=contributors[i].role);
  }
}