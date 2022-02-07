$(document).ready(function() {

  if (pilotMode) {
  // Do not pre-fill the subject terms
  }
  else{
      console.log('genres', genres);

      genreCategories = ['brinkman_vorm', 'CBK_genre'];
      for (var category of genreCategories){
        listOfGenres = genres[category];
        table_name = category.includes('brinkman')? 'brinkman':category
        for (var subject of listOfGenres){
            subjectString = subject['identifier']+' - '+subject['term'];
            addSubjectRow(table_name, 'vorm', subject['term'], subject['identifier']);
        }
      }
      subjectCategories = ['brinkman_zaak'];
      for (var category of subjectCategories){
        listOfSubjects = subjects[category];
        table_name = category.includes('brinkman')? 'brinkman':category
        for (var subject of listOfSubjects){
            addSubjectRow(table_name, 'kind', subject['term'], subject['identifier']);
        }
      }
    }

  $('#no-results').hide();
  clearResults();
  $('#button-clear').click(function() {
    $('#text').val('');
    $('#text').focus();
    });

    var ann_results = $('#annif-results-table').DataTable( {
      paging: false,
      searching: false,
      info: false,
      columnDefs: [
        {width: 500, targets: 0 }
      ],
      fixedColumns: true,
      ordering: false
      });
    $('#annif-results-table').parents('div.dataTables_wrapper').first().hide();

});

function addSubjectRow(category, kind, subjectTerm, identifier){
  $("#"+category+"-table > tbody").append($('<tr align=center>')
    .append($('<td>').append('<input onclick="delete_row(this);" type="button" value="&#xf2ed" class="fas fa-trash-alt" title="Verwijder onderwerp">'))
    .append($('<td>').append('<input onclick="move_row(this,1);" type="button" value="&#xf062" class="fas fa-arrow-up" title="Verplaats omhoog">'))
    .append($('<td>').append('<input onclick="move_row(this,0);" type="button" value="&#xf063" class="fas fa-arrow-down" title="Verplaats omlaag">'))
    .append($('<td class="name_cell">').append('<div class="subjectbox '+kind+'" data-identifier="'+identifier+'">'+subjectTerm+'</div>')));
}


var annif_url = 'https://kbresearch.nl/annif/v1/';

function clearResults() {
    $("#annif-results-table > tbody").empty();
    $('#annif-results-table').css('visibility', 'hidden');
}

function fetchProjects() {
    console.log('Fetching projects');
    $.ajax({
        url: '/annif-projects',
        success: function(data){
            console.log(data);
            $('#project').empty();
            $.each(data.projects, function(idx, value) {
                $('#project').append(
                    $('<option>').attr('value',value.project_id).append(value.name)
                    );
            });
        },
        error: function(error) {
          console.log(error);
      }
  });
}

function getSuggestions(project, category, subcategory) {
    inputtext = $('#publication_title').text().replace('@','');
    inputtext += $('#publication_summary').text();

    console.log('inputtext: ', inputtext);
    $.ajax({
        url: '/annif-suggestions',
        data: {
          text: inputtext,
          project: project,
          limit: 20,
          threshold: 0.001
      },
      success: function(data) {
        clearResults();
        console.log(data.results);
        if (data.results.length == 0) {
            $('#suggestions').text('Geen resultaten gevonden');
            $('#suggestions').css('visibility', 'visible');
        }
        else {
            displayResults(data.results, category, subcategory);
        }
    }
});
}


function displayResults(resultList, category, subcategory) {
    $('#no-results').css('visibility', 'hidden');
    $('#suggestions').text('Voorgestelde trefwoorden ('+category+')');
    $('#suggestions').css('visibility', 'visible');
    $('#annif-results-table').css('visibility', 'visible');
    $.each(resultList, function(idx, value) {
      identifier = value.uri.split('/p').slice(-1);
      term = value.label;
      color=getColorForPercentage(value.score);
      $('#annif-results-table > tbody').append(
        $('<tr onclick="addSubjectRow(\''+category+'\',\''+subcategory+'\',\''+ term+'\',\''+ identifier+'\')" title="Selecteer term">')
        .append($('<td >')
                 .text(term)
                )
        .append($('<td class="match_cell" style="background-color:'+color+'">').text(Math.round(value.score * 1000)/10))
        );
  });
    $('#annif-results-table').parents('div.dataTables_wrapper').first().show();
}
