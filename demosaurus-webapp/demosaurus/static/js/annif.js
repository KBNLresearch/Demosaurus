
var base_url = 'https://kbresearch.nl/annif/v1/';

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

function getSuggestions(project, category) {
    inputtext = $('#publication_title').text();
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
            displayResults(data.results, category);
        }
    }
});
}


function displayResults(resultList, category) {
    $('#no-results').css('visibility', 'hidden');
    $('#suggestions').text('Voorgestelde trefwoorden ('+category+')');
    $('#suggestions').css('visibility', 'visible');
    $('#annif-results-table').css('visibility', 'visible');
    $.each(resultList, function(idx, value) {
      identifier = value.uri.split('/').slice(-1);
      term = value.label;
      color=getColorForPercentage(value.score);
      $('#annif-results-table > tbody').append(
        $('<tr onclick="addSubjectRow(\''+category+'\',\''+ term+'\',\''+ identifier+'\')" title="Selecteer term">')
        .append($('<td >')
                 .text(term)
                )
        .append($('<td class="match_cell" style="background-color:'+color+'">').text(Math.round(value.score * 1000)/10))
        );
  });
    $('#annif-results-table').parents('div.dataTables_wrapper').first().show();
}

$(document).ready(function() {
    $('#no-results').hide();
    clearResults();
        //fetchProjects();

        $('#button-clear').click(function() {
            $('#text').val('');
            $('#text').focus();
        });
    });