function callIsQueryExported(startDate, endDate, query, selectedValue) {
  document.getElementById("universalSearch2").value = "";
  dataTable2.row.add([selectedValue, query, startDate, endDate]).draw(false);
  var x = document.getElementById("SuggestionDivDisplay");
  x.style.display = "block";
}

function submitQuery(params) {
  const start_date = $("#democonfigstart").val();
  const end_date = $("#democonfigend").val();

  const ipArray = [];
  const userArray = [];
  const hostArray = [];

  const structureData =
    params &&
    params.map((item, index) => {
      if (item[0] === "IP") {
        ipArray.push(item[1]);
      } else if (item[0] === "user") {
        userArray.push(item[1]);
      } else if (item[0] === "host") {
        hostArray.push(item[1]);
      }
    });

  $("#cover-spin").show(0);
  var request = new XMLHttpRequest();
  request.open("POST", `${rootUrl}/isQueryExported`);
  request.setRequestHeader("cache-control", "no-cache");
  request.setRequestHeader("Content-Type", "application/json");
  request.setRequestHeader("Access-Control-Allow-Origin", "*");
  request.setRequestHeader(
    "Access-Control-Allow-Headers",
    "authorization, content-type"
  );

  request.onload = function () {
    if (this.readyState == this.DONE) {
      $("#cover-spin").hide(0);
      const testData = JSON.parse(this.response);
      if (testData.status === true) {
        localStorage.setItem("case_id", testData.caseId);
        const aa = `<div><a href="${redirectUrl}" target="blank">View Graph</a></div>`;
        $("#exampleModal").modal("show");
        $("#errorDes").text(
          `Case id already exists to view click on the button view graph for the case id : ${testData.caseId}`
        );
        $("#errorDescode").html(aa);
        document.getElementById("universalSearch2").value = "";
        var x = document.getElementById("SuggestionDivDisplay");
        x.style.display = "none";
        // dataTable2.clear().draw();
      } else {
        $("#startExportbtn").css({ display: "block" });
        $("#exampleModal").modal("show");
        $("#errorDes").text(
          `Case does not exists to start export click on the case id`
        );
        var x = document.getElementById("SuggestionDivDisplay");
        x.style.display = "none";
      }
    } else {
      $("#cover-spin").hide(0);
    }
  };

  const finalSelectedSources = [];
  const activeSourceSelected = localStorage.getItem("activeSources");

  if (activeSourceSelected.length === 5) {
    finalSelectedSources.push("all");
  }

  var requestdata = JSON.stringify({
    startDate: start_date,
    endDate: end_date,
    dataSource:
      finalSelectedSources.length > 0
        ? finalSelectedSources
        : activeSourceSelected,
    query: {
      IP: {
        entityQueries: ipArray,
      },
      user: {
        entityQueries: userArray,
      },
      host: {
        entityQueries: hostArray,
      },
    },
  });
  request.send(requestdata);
}

function startExportingCase(abc) {
  $("#cover-spin").show(0);
  alert("Export Started in Background");

  const start_date = $("#democonfigstart").val();
  const end_date = $("#democonfigend").val();

  const ipArray = [];
  const userArray = [];
  const hostArray = [];
  var params2 = abc;
  const structureData =
    params2 &&
    params2.map((item, index) => {
      if (item[0] === "IP") {
        ipArray.push(item[1]);
      } else if (item[0] === "user") {
        userArray.push(item[1]);
      } else if (item[0] === "host") {
        hostArray.push(item[1]);
      }
    });

  var request = new XMLHttpRequest();
  // Open a new connection, using the POST request on the URL endpoint
  request.open("POST", `${rootUrl}/startCaseExport`);
  request.setRequestHeader("cache-control", "no-cache");
  request.setRequestHeader("Content-Type", "application/json");

  request.setRequestHeader("Access-Control-Allow-Origin", "*");
  request.setRequestHeader(
    "Access-Control-Allow-Headers",
    "authorization, content-type"
  );

  request.onload = function () {
    if (this.readyState == this.DONE) {
      $("#cover-spin").hide(0);
      const testData = JSON.parse(this.response);
      // check what all comes
      appendDataToCaseTable(
        testData.caseId,
        start_date,
        end_date,
        ipArray,
        userArray,
        hostArray
      );
    }
  };
  var requestdata = JSON.stringify({
    startTime: start_date,
    endTime: end_date,
    dataSource: ["watchguard"],
    query: {
      IP: {
        entityQueries: ipArray,
      },
      user: {
        entityQueries: userArray,
      },
      host: {
        entityQueries: hostArray,
      },
    },
  });
  request.send(requestdata);
}

function appendDataToCaseTable(
  caseId,
  start_date,
  end_date,
  ipArray,
  userArray,
  hostArray
) {
  var testattay = [
    {
      case_id: caseId,
      status: "Started Export",
      nodes: "-",
      query: {
        IP: ipArray,
        Users: userArray,
        Host: hostArray,
      },
      startTime: start_date,
      endTime: end_date,
      source: "All",
      exportTime: "-",
      dataSources: "All",
      processingTime: "-",
    },
  ];

  document.getElementById("universalSearch2").value = "";

  callInitialCaseStatus(testattay, "filterdType");

  // $("#filtertable").DataTable().row.add(testattay).draw(false);
  var x = document.getElementById("SuggestionDivDisplay");
  x.style.display = "none";
  dataTable2.clear().draw();
}

var $overlay = $(".overlay"),
  $overlayTrigger = $(".overlay-trigger"),
  $overlayClose = $(".overlay-close"),
  openClass = "is-open";

$overlayTrigger.on("click", function () {
  var num = ("0" + ($(this).index() + 1)).slice(-2);
  $(".overlay" + num).addClass(openClass);
  $overlayClose.addClass(openClass);
});

$overlayClose.on("click", function () {
  $overlayClose.removeClass(openClass);
  $overlay.removeClass(openClass);
});

$overlay.on("click", function () {
  $overlayClose.removeClass(openClass);
  $overlay.removeClass(openClass);
  hideSuggestionBox();
});

$(".closeModal").on("click", function () {
  $(".overlay-close").removeClass(openClass);
  $(".overlay").removeClass(openClass);
});
