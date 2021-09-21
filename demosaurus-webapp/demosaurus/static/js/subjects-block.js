$(document).ready(function() {

  console.log(genres);

  genreCategories = ['brinkman', 'CBK_genre'];
  for (var category of genreCategories){
    listOfsubjects = genres[category];
    for (var subject of listOfsubjects){
        addSubjectRow(category, 'vorm', subject['term'], subject['identifier']);
    }
  }

   subjectCategories = ['brinkman'];
  for (var category of subjectCategories){
    listOfsubjects = subjects[category];
    for (var subject of listOfsubjects){
        addSubjectRow(category, 'zaak', subject['term'], subject['identifier']);
    }
  }

});

function addSubjectRow(category, kind, subjectTerm, identifier){
  $("#"+category+"-table > tbody").append($('<tr align=center>')
    .append($('<td>').append('<input onclick="delete_row(this);" type="button" value="&#xf2ed" class="fas fa-trash-alt" title="Verwijder onderwerp">'))
    .append($('<td>').append('<input onclick="move_row(this,1);" type="button" value="&#xf062" class="fas fa-arrow-up" title="Verplaats omhoog">'))
    .append($('<td>').append('<input onclick="move_row(this,0);" type="button" value="&#xf063" class="fas fa-arrow-down" title="Verplaats omlaag">'))
    .append($('<td class="name_cell">').append('<div class="subjectbox '+kind+'">'+subjectTerm+'</div>')));
}