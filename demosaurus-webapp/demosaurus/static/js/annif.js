
var base_url = 'https://kbresearch.nl/annif/v1/';

function clearResults() {
    //tbannif.clear();
    $("#annif-results-table tbody").empty();
    $('#suggestions').hide();
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

function getSuggestions() {
    console.log($('#text').val());
    $('#suggestions').show();
    $.ajax({
        url: '/annif-suggestions',
        data: {
          text: $('#text').val(),
          project: $('#project').val(), 
          limit: 20, 
          threshold: 0.001
        },
        success: function(data) {
            if (data.results.length == 0) {
                $('#results').hide();
                $('#no-results').show();
            }
            $.each(data.results, function(idx, value) {
                $('#no-results').hide();
                /*
                $('#results').append(
                    $('<li class="list-group-item p-0">').append(
                        $('<meter class="mr-2">').attr('value',value.score).attr('max',1.0).attr('title',value.score.toFixed(4)),
                        $('<a target="_blank">').attr('href',value.uri).append(value.label)
                    )
                );
                */
                $('#annif-results-table > tbody').append(
                    $('<tr>')
                    .append($('<td>').append($('<a target="_blank">').attr('href',value.uri).append(value.label)))
                    .append($('<td class="match_cell">').append($('<div>').css("background-color",getColorForPercentage(value.score)).text(Math.round(value.score * 1000)/10))));

                //$('#annif-results-table').DataTable();
                //tbannif.draw();
                



                //$('#results').show();
            });
        }
    });
}

function disableButton() {
    $('#get-suggestions').prop("disabled", true);
}

function enableButton() {
    $('#get-suggestions').prop("disabled", false);
}

$(document).ready(function() {
    $('#no-results').hide();
    clearResults();
    if ($.trim($('#text').val()) != "") {
        enableButton();
    } else {
        disableButton();
    }
    fetchProjects();
    $('#get-suggestions').click(function() {
        clearResults();
        getSuggestions();
        $('#annif-results-table').parents('div.dataTables_wrapper').first().show();
    });
    $('#button-clear').click(function() {
        $('#text').val('');
        $('#text').focus();
        clearResults();
        disableButton();
    });
    $('#text').on("input", function() {
        enableButton();
    });
});
