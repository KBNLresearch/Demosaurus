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

    //console.log($('#main_'+id).is(':checked'));

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
    export_keywords();
  }


function export_keywords() {
  var br_kmc = 5200
  var cbk_kmc = 5560

  // Get Brinkman and CBK data from tables.
  var br_keywords = []
  var cbk_keywords = []

  $('#brinkman-table .subjectbox').each(function(i, elem) {
    br_keywords.push($(this).text())
  });
  $('#CBK_genre-table .subjectbox').each(function(i, elem) {
    cbk_keywords.push($(this).text())
  });

  // Create KMC lines for WinIBW.
  let text = "";
  if (br_keywords || cbk_keyword) {
    $('#general_content').css("display","block");
    
    br_keywords.forEach(br_kmc_html);
    cbk_keywords.forEach(cbr_kmc_html)
    
    function br_kmc_html(val, index, array) {
      br_kmc += index;
      var i = val.lastIndexOf('-');
      br_id = val.substring(i+2);
      br_desc = val.substring(0, i);
      text += "<p>" + br_kmc + "\t!" + br_id + "!" + br_desc + "</p>";
    }

    function cbr_kmc_html(val, index) {
      cbk_kmc += index;
      var i = val.lastIndexOf('-');
      cbk_id = val.substring(i+2);
      cbk_desc = val.substring(0, i);
      text += "<p>" + cbk_kmc + "\t!" + cbk_id + "!" + cbk_desc + "</p>";
    }
    
    $('#general_content').html(text);
  };
  console.log(br_keywords.length)
  if (br_keywords.length === 0){
    //text += "<p>Let op: Geen Brinkman trefwoorden gekozen!</p>";
    $('#subject_tab_flag').css("visibility","visible");
    $('#message').append('</br><i>&#8226; Let op: Geen Brinkman trefwoorden gekozen!</i></br>');
  };
  if (cbk_keywords.length === 0){
    //text += "<p>Let op: Geen CBK trewoorden gekozen!</p>"
    $('#subject_tab_flag').css("visibility","visible");
    $('#export > #message').append('</br><i>&#8226; Let op: Geen CBK trefwoorden gekozen!</i></br>');
  };

};
