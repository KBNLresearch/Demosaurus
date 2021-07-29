function export_info() {
  console.log('Export button')

  deactivate_rows();
  $("#export > #message").empty();

  var allroles = true;
  var allppns = true;

  var contributors = [];
  var all_kmcs = '';

  // build up kmc contents for contributors: contributorname$role$!ppn!viafname
  var rows = $('#contributortable > tbody > tr');
  var at_kmc = 3011;
  for (var i=0; i < rows.length; i++) {
    var id = rows[i].id.split('_')[1];
    console.log('row', id);

    console.log($('#main_'+id).is(':checked'));



    if (i==0 && $('#main_'+id).is(':checked')){
      all_kmcs += '<p>3000\t';
    }
    else {
      all_kmcs += "<p>"+at_kmc+"\t";
      if (at_kmc <3019) {
        at_kmc ++;
      }
    }

    all_kmcs += $('#aut_name_'+id).val();
    role = $('#role_'+id).val();
    if (role) {
        role = role.replace(/(^.*\[|\].*$)/g, ''); // get the role-code bit
        all_kmcs += '$'+ role +'$';
      }
      else {
        $('#role_'+id).css("backgroundColor","red");
        allroles = false;
      }

      ppn = $('#ppn_'+id).val();
      if (ppn) {
        all_kmcs += '!'+ ppn +'!';
      }
      else {
        $('#ppn_'+id).css("backgroundColor","red");
        allppns = false;
      }
      all_kmcs += "</p>";
    }

    $('#contributors_tab_flag').css("visibility","hidden");

    // Report about the completeness of the input
    if (! allroles) {
        $('#contributors_tab_flag').css("visibility","visible");
        $('#export > #message').append('<br><i>&#8226; Let op: niet bij alle auteurs is de rol ingevoerd!</i></br>');
      }
    if (! allppns) {
        $('#contributors_tab_flag').css("visibility","visible");
        $('#export > #message').append('<br><i>&#8226; Let op: niet alle auteurs zijn gethesaureerd!</i></br>');
      }

      $('#thesaureer_title').text('KMCS:');
      //$("#candidate_list > thead").empty();
      //$("#candidate_list > tbody").empty();


    // Serve collected information in the web application
    // NB todo: export primary author (if they exist) to KMC 3000 rather than 3011
    $('#export_content').html(all_kmcs);
  }
