"use strict";

ckan.module('evaluator_goodtables', function ($, _) {
  return {
    initialize: function () {
      const datasetUrl = $("#dataset_url").val()
      const goodTableUrl = 'http://goodtables.okfnlabs.org/api/run?data_url=' + datasetUrl;
      const linkToGT = "<a class='muted' href='http://goodtables.okfnlabs.org/reports?data_url="+datasetUrl+"' target='_blank'>ver en Good Tables </a>";

      $.get(goodTableUrl)
        .done((data) => {
          let gt_status = $("#gt_status");

          if (!data.success) {
            gt_status.addClass('text-error');
            gt_status.html('in valid');
            createGoodTableResults(data.report.results);
          } else {
            gt_status.addClass('text-success');
            gt_status.html('valid');
          }

          $("#resultsTable").append(linkToGT);
        });

      let createGoodTableResults = (results) => {
        let resultsTable = $("#resultsTable");
        let table = "<table id='errorTable' class='table table-condensed table-hover'><thead><tr><th>fila</th><th>nombre</th><th>descripción</th></tr></thead><tbody></tbody></table>";

        resultsTable.html(table);

        let errorTable = $("#errorTable");
        for (let result in results) {
          let res = results[result];
          for (let key in res) {
            let err_row = res[key].row_index;
            let err_name = res[key].results[0].result_name;
            let err_msg = res[key].results[0].result_message;
            let err_lvl = res[key].results[0].result_level;
            let row = "<tr class='"+err_lvl+"'><td>"+err_row+"</td><td>"+err_lvl+" - "+err_name+"</td><td>"+err_msg+"</td></tr>";

            errorTable.append(row);
          }
        }



      }
    }
  };
});
