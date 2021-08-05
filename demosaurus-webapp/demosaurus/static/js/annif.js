
var base_url = 'https://kbresearch.nl/annif/v1/';

function clearResults() {
    $("#annif-results-table > tbody").empty();
    $('#suggestions').hide();
    $('#annif-results-table').hide();
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
    console.log($('#text').val());
    $.ajax({
        url: '/annif-suggestions',
        data: {
          text: $('#text').val(),
          project: project,
          limit: 20, 
          threshold: 0.001
      },
      success: function(data) {
        clearResults();
        console.log(data.results);
        if (data.results.length == 0) {
            $('#no-results').show();
        }
        else {
            displayResults(data.results, category);
        }
    }
});
}


function displayResults(resultList, category) {
    $('#no-results').hide();
    $('#suggestions').text('Voorgestelde trefwoorden ('+category+')');
    $('#suggestions').show();
    $('#annif-results-table').show();
    $.each(resultList, function(idx, value) {
      identifier = value.uri.split('/').slice(-1);
      term = value.label;     
      $('#annif-results-table > tbody').append(
        $('<tr>')
        .append($('<td>')
            .append($('<a class="action" title="Selecteer term" href="#" onclick="addSubjectRow(\''+category+'\',\''+ term+'\',\''+ identifier+'\')">')
                .text(identifier)
                ))
        .append($('<td>').append($('<a target="_blank">').attr('href',value.uri).append(term)))
        .append($('<td class="match_cell">').append($('<div>').css("background-color",getColorForPercentage(value.score)).text(Math.round(value.score * 1000)/10)))
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