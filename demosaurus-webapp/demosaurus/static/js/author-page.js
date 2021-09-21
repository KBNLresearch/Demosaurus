// Fill HTML table on authorpage.html

function add_to_publication_list(publications, authorname, role){

  $("#publication_list > thead").append($('<tr>')
                .append($('<th scope="col" >').text('PPN'))
                .append($('<th scope="col" >').text('Titelvermelding'))
                .append($('<th scope="col" >').text('Verantwoordelijkheidsvermelding'))
                .append($('<th scope="col" >').text('Bijdrage '+authorname))
                );

  for(var i = 0; i< publications.length; i++){
            var row = publications[i];

    $("#publication_list > tbody").append($('<tr>')
      .append($('<td class="ppn_cell" >').text(row.publication_ppn))
      .append($('<td class="title_cell" >').text(row.titelvermelding))
      .append($('<td class="title_cell" >').text(row.verantwoordelijkheidsvermelding))
      .append($('<td id="role_'+i+'" class="title_cell" >').text(row.role)));
      if (row.role!=role){
        $('#role_'+i).css("background-color",getColorForPercentage(1.0));
      }
  }

}
