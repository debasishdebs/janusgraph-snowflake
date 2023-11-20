var dataTable;
var tableData = [];

$(document).ready(function () {
  getAllCaseIds("start");
  document.getElementById("tabnameseleted").value = "user";
  localStorage.setItem("activeSources", null);
});

window.setInterval(function () {
  getAllCaseIds("regular");
}, 60000);

function getAllCaseIds(initialStatus) {
  if (initialStatus === "start") {
    $("#cover-spin").show(0);
  }
  var request = new XMLHttpRequest();
  // Open a new connection, using the POST request on the URL endpoint
  request.open("POST", `${rootUrl}/getAllCaseIds`);
  request.setRequestHeader("cache-control", "no-cache");
  request.setRequestHeader("Content-Type", "application/json");

  request.setRequestHeader("Access-Control-Allow-Origin", "*");
  request.setRequestHeader(
    "Access-Control-Allow-Headers",
    "authorization, content-type"
  );

  request.onload = function () {
    if (this.readyState == this.DONE) {
      if (initialStatus === "start") {
        $("#cover-spin").hide(0);
      }
      const testData = JSON.parse(this.response);
      const filtered = testData.case_ids.filter(function (el) {
        return el != "";
      });
      filtered && filtered.length > 0 && refreshcall(filtered, initialStatus);
    }
  };

  request.send();
}

function refreshcall(listarr, initialStatus) {
  if (listarr.length > 0) {
    callIni(
      {
        case_id: listarr,
      },
      "removedata",
      initialStatus
    );
  } else {
    callIni(
      {
        case_id: ["159968_sstech_5900.2642250061035"],
      },
      "static",
      initialStatus
    );
  }
}

function callIni(payload, typeofAppend, initialStatus) {
  if (initialStatus === "start") {
    $("#cover-spin").show(0);
  }
  var request = new XMLHttpRequest();
  request.open("POST", `${rootUrl}/getCaseStatus`);
  request.setRequestHeader("cache-control", "no-cache");
  request.setRequestHeader("Content-Type", "application/json");
  request.setRequestHeader("Access-Control-Allow-Origin", "*");
  request.setRequestHeader(
    "Access-Control-Allow-Headers",
    "authorization, content-type"
  );

  request.onload = function () {
    if (this.readyState == this.DONE) {
      if (initialStatus === "start") {
        $("#cover-spin").hide(0);
      }
      const testData = JSON.parse(this.response);
      callInitialCaseStatus(testData, "unsort", typeofAppend);
    } else {
      $("#cover-spin").hide(0);
    }
  };

  var requestdata = JSON.stringify(payload);
  request.send(requestdata);
}

function callInitialCaseStatus(newData, type, typeofAppend) {
  let tempData = [];
  if (type === "unsort") {
    tempData = Object.values(newData).map(({ others, ...x }) =>
      Object.assign(x, others)
    );
  } else {
    tempData = newData;
  }

  if (typeofAppend === "removedata") {
    tableData = [];
  }
  if (JSON.stringify(tableData) !== JSON.stringify(tempData)) {
    tableData.push(...tempData);
  }

  dataTable.clear();
  dataTable.rows.add([...new Set(tableData)]).draw();
}

dataTable = $("#filtertable").DataTable({
  data: tableData,
  columnDefs: [
    { width: "5%", targets: 4 },
    { width: "5%", targets: 7 },
  ],
  order: [[1, "asc"]],
  columns: [
    {
      data: "case_id",
      render: function (data, type, row, meta) {
        if (
          row.status == "Export Complete" ||
          row.status == "Data Load Complete" ||
          row.status == "Completed"
        ) {
          return `<a class="redirectThreatHunt" href="${redirectUrl}" target="blank" style="cursor: pointer;">${data}</a>`;
        } else {
          return data;
        }
      },
    },
    { data: "status" },
    {
      data: "query",
      render: function (data, type, row, meta) {
        return `<a class="viewQuery" style="cursor: pointer;">View Query</a>`;
      },
    },
    {
      data: "exportTime",
    },
    { data: "nodes" },
    {
      data: "startTime",
      render: function (data, type, row, meta) {
        return data ? data : "-";
      },
    },
    {
      data: "endTime",
      render: function (data, type, row, meta) {
        return data ? data : "-";
      },
    },
    {
      data: "dataSources",
      render: function (data, type, row, meta) {
        return data && data.length > 0
          ? data.join() === "all"
            ? "All"
            : data.join()
          : "-";
      },
    },
    {
      data: "processingTime",
    },
  ],
  processing: true,
  responsive: true,
  paging: true,
  ordering: true,
  info: false,
  bPaginate: false,
  bLengthChange: false,
  pageLength: 5,
  dom: '<"top">ct<"top"p><"clear">',
});

$("#filterbox").keyup(function () {
  dataTable.search(this.value).draw();
});
// Column level filter
$("#filtertable thead tr").clone().appendTo("#filtertable thead");
$("#filtertable thead tr:eq(1) th").css("padding", "5px");
$("#filtertable thead tr:eq(1) th").each(function (i) {
  var title = $(this).text();
  $(this).html(
    '<input type="text" placeholder="Search..." class="search-bar"/>'
  );
  $("input", this).on("keyup change", function () {
    if (dataTable.column(i).search() !== this.value) {
      dataTable.column(i).search(this.value).draw();
    }
  });
});

var dataTable2 = $("#filtertable2").DataTable({
  paging: false,
  ordering: true,
  info: false,
  searching: false,
});

const btn = document.querySelector(".tabs");
// handle click button
btn.onclick = function () {
  const rbs = document.querySelectorAll('input[name="tab-control"]');
  let selectedValue;
  for (const rb of rbs) {
    if (rb.checked) {
      selectedValue = rb.value;
      break;
    }
  }
  document.getElementById("tabnameseleted").value = selectedValue;
};

$("#addRow").on("click", function () {
  const universalSearchParam = $("#universalSearch2").val();
  const start_date = $("#democonfigstart").val();
  const end_date = $("#democonfigend").val();
  const tabNameParam = $("#tabnameseleted").val();
  const activeSourcesSession = localStorage.getItem("activeSources");

  if (universalSearchParam !== "" && start_date !== "" && end_date !== "") {
    if (activeSourcesSession !== "null") {
      callIsQueryExported(
        start_date,
        end_date,
        universalSearchParam,
        tabNameParam
      );
    } else {
      alert("Select data sources to proceed");
    }
  } else {
    alert(
      "Add Query parameter and select a date , source type  and type of search to proceed"
    );
  }
});

function hideSuggestionBox() {
  var x = document.getElementById("SuggestionDivDisplay");
  x.style.display = "none";
  dataTable2.clear().draw();
}

function submitButtn() {
  const universalSearchParam = $("#universalSearch2").val();
  const start_date = $("#democonfigstart").val();
  const end_date = $("#democonfigend").val();
  const tabNameParam = $("#tabnameseleted").val();
  const activeSourcesSession = localStorage.getItem("activeSources");

  if (universalSearchParam !== "" && start_date !== "" && end_date !== "") {
    if (activeSourcesSession !== "null") {
      var x = document.getElementById("SuggestionDivDisplay");
      x.style.display = "none";
      submitQuery(dataTable2.rows().data().toArray());
    } else {
      alert("Select data sources to proceed");
    }
  } else {
    alert(
      "Add Query parameter and select a date , source type  and type of search to proceed"
    );
  }
}

function ShowSuggesion() {
  var x = document.getElementById("SuggestionDivDisplay");
  x.style.display = "block";
}

// Source Filter
function casecheckBoxValidation() {
  let caseactiveSources = [];
  $("#casesemanticSource").prop("checked") && caseactiveSources.push("sepc");
  $("#casewatchgSource").prop("checked") &&
    caseactiveSources.push("watchguard");
  $("#casewindowsSource").prop("checked") && caseactiveSources.push("windows");
  $("#casesysmon").prop("checked") && caseactiveSources.push("sysmon");
  $("#casemsExchange").prop("checked") && caseactiveSources.push("msexchange");

  localStorage.setItem("activeSources", JSON.stringify(caseactiveSources));
}

// Calling Checkbox source filter
$(document).on("click", "input[type='checkbox']", function (e) {
  casecheckBoxValidation();
});

$("#filtertable tbody").on("click", ".viewQuery", function () {
  var data = dataTable.row($(this).parents("tr")).data();
  $("#exampleModal").modal("show");
  $("#errorDes").text("Query for Case Id :" + data.case_id);
  // data.query && data.query.Users.length > 0
  //   ? data.query.Users.join(",<br/>")
  //   : ""

  var codeDiv = "";

  $("#errorDescode").html(codeDiv);
});

$("#filtertable tbody").on("click", ".redirectThreatHunt", function () {
  var data = dataTable.row($(this).parents("tr")).data();
  localStorage.setItem("case_id", data.case_id);
});
