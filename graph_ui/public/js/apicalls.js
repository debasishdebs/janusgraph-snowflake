//Drill Down Function
function getDrilldowndata(newData) {
  d3.select(".legends").selectAll("*").remove();
  $("#cover-spin").show(0);
  $("#universalsearch").val("");

  localStorage.setItem("id", newData.node_id);
  console.log("ID Stored: ", localStorage.getItem("id"));
  var request = new XMLHttpRequest();

  var url = `${rootUrl}/getGraphForId`;
  // Open a new connection, using the POST request on the URL endpoint

  if (SessionArray.length !== 0) {
    document.getElementById("backBtn").style.display = "inline";
    document.getElementById("forwardBtn").style.display = "inline";
  }
  SessionPointer = SessionPointer + 1;

  if (SessionArray.length === SessionPointer) {
    document.getElementById("forwardBtn").style.display = "none";
  }

  request.open("POST", url);
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
      console.log(JSON.parse(this.response), "data");
      // if(JSON.parse(this.response).data.nodes.length > 100){
      //     getTreeData(url)
      // }else{
      getData(JSON.parse(this.response));
      populateCounter(JSON.parse(this.response));
      // }
    }
  };
  const newObj = {
    id: newData.node_id,
    dedup: "true",
    hops: 1,
  };
  const requestdata = JSON.stringify(newObj);

  if (SessionPointer !== SessionArray.length) {
    SessionArray.splice(SessionPointer, 0, url);
    idHere.splice(SessionPointer, 0, newObj);
  } else {
    SessionArray.push(url);
    idHere.push(newObj);
  }

  request.send(requestdata);
}

// Universal search function
$(".search-label").click(function () {
  const searchTypeTerm = localStorage.getItem("typeOfSearch");
  if (searchTypeTerm != "") {
    $("#cover-spin").show(0);
    localStorage.removeItem("id");
    d3.select(".cichart").selectAll("*").remove();
    d3.select(".legends").selectAll("*").remove();
    var searchVal = document.getElementById("universalsearch").value;

    var API_URL;
    if (searchVal.includes("http://")) {
      API_URL = searchVal;
    } else if (localStorage.setItem("searchVal", searchVal) !== undefined) {
      localStorage.setItem("searchVal", searchVal);
      API_URL = `${rootUrl}/getGraphForProperty`;
    } else {
      API_URL = `${rootUrl}/getGraphForProperty`;
    }
    const idData = localStorage.getItem("id");

    var request = new XMLHttpRequest();
    // Open a new connection, using the POST request on the URL endpoint
    request.open("POST", API_URL);
    if (SessionArray.length !== 0) {
      document.getElementById("backBtn").style.display = "inline";
      document.getElementById("forwardBtn").style.display = "inline";
    }

    SessionPointer = SessionPointer + 1;

    if (SessionArray.length === SessionPointer) {
      document.getElementById("forwardBtn").style.display = "none";
    }

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
        var checkData = JSON.parse(this.response);
        if (checkData.edges.length > 0) {
          getData(JSON.parse(this.response));
          populateCounter(JSON.parse(this.response));
        } else {
          $("#exampleModal").modal("show");
          $("#errorDes").text("No data found");
        }
      }
    };
    let typeOfSearch = localStorage.getItem("typeOfSearch");
    const objVal = {
      search_for: typeOfSearch,
      search_value: searchVal,
      dedup: "true",
      hops: 1,
    };
    var requestdata = JSON.stringify(objVal);

    if (SessionPointer !== SessionArray.length) {
      SessionArray.splice(SessionPointer, 0, API_URL);
      idHere.splice(SessionPointer, 0, objVal);
    } else {
      SessionArray.push(API_URL);
      idHere.push(objVal);
    }

    request.send(requestdata);
  } else {
    alert("Select type of search entity");
  }
});

// Source Filter
function checkBoxValidation() {
  $("#cover-spin").show(0);
  let link;

  let activeSources = [];
  $("#semanticSource").prop("checked") && activeSources.push("sepc");
  $("#watchgSource").prop("checked") && activeSources.push("watchguard");
  $("#windowsSource").prop("checked") && activeSources.push("windows");
  $("#sysmon").prop("checked") && activeSources.push("sysmon");
  $("#msExchange").prop("checked") && activeSources.push("msexchange");

  console.log(activeSources);
  d3.select(".cichart").selectAll("*").remove();
  d3.select(".legends").selectAll("*").remove();
  let requestdata = {};
  var location = window.location.href;
  var url = new URL(location);
  var search_for = url.searchParams.get("for");

  console.log(search_for, "search_for");

  if (url.searchParams.get("graph")) {
    graphVar = url.searchParams.get("graph");
  }

  let sessionId = localStorage.getItem("id");
  let typeOfSearch = localStorage.getItem("typeOfSearch");
  let searchVal = document.getElementById("universalsearch").value;
  let caseIdVal = localStorage.getItem("case_id");

  if (search_for !== null) {
    link = `${rootUrl}/getGraphForProperty`;
  } else {
    let sessionSDate = localStorage.getItem("startDate");
    let sessionEDate = localStorage.getItem("endDate");
    if (sessionSDate && sessionEDate) {
      sessionSDate = sessionSDate.substr(0, 24);
      sessionEDate = sessionEDate.substr(0, 24);
    }
    console.log("selected dates ", sessionEDate, sessionSDate);

    if (sessionSDate && sessionEDate) {
      if (caseIdVal) {
        link = `${rootUrl}/getGraphForCaseId`;
        requestdata = {
          startTime: sessionSDate,
          endTime: sessionEDate,
          caseId: caseIdVal,
          data_source_name: activeSources.join(),
          dedup: true,
        };
      } else if (sessionId != null) {
        link = `${rootUrl}/getGraphForId`;
        requestdata = {
          startTime: sessionSDate,
          endTime: sessionEDate,
          id: Number(sessionId),
          data_source_name: activeSources.join(),
        };
      } else if (searchVal != "") {
        link = `${rootUrl}/getGraphForProperty`;
        requestdata = {
          startTime: sessionSDate,
          endTime: sessionEDate,
          search_for: typeOfSearch,
          search_value: searchVal,
          data_source_name: activeSources.join(),
        };
      } else {
        console.log("Error");
        $("#exampleModal").modal("show");
        $("#errorDes").text("No data found");
      }
    } else {
      if (caseIdVal) {
        link = `${rootUrl}/getGraphForCaseId`;
        requestdata = {
          caseId: caseIdVal,
          data_source_name: activeSources.join(),
          dedup: true,
        };
      } else if (sessionId != null) {
        link = `${rootUrl}/getGraphForId`;
        requestdata = {
          id: Number(sessionId),
          data_source_name: activeSources.join(),
        };
      } else if (searchVal != "") {
        link = `${rootUrl}/getGraphForProperty`;
        requestdata = {
          search_for: typeOfSearch,
          search_value: searchVal,
          data_source_name: activeSources.join(),
        };
      } else {
        console.log("Error");
        $("#exampleModal").modal("show");
        $("#errorDes").text("No data found");
      }
    }
  }

  if (SessionArray.length !== 0) {
    document.getElementById("backBtn").style.display = "inline";
    document.getElementById("forwardBtn").style.display = "inline";
  }
  SessionPointer = SessionPointer + 1;

  if (SessionArray.length === SessionPointer) {
    document.getElementById("forwardBtn").style.display = "none";
  }

  var request = new XMLHttpRequest();
  // Open a new connection, using the POST request on the URL endpoint
  request.open("POST", link);
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
      getData(JSON.parse(this.response));
      populateCounter(JSON.parse(this.response));
    } else {
      // put error
    }
  };

  if (SessionPointer !== SessionArray.length) {
    SessionArray.splice(SessionPointer, 0, link);
    idHere.splice(SessionPointer, 0, requestdata);
  } else {
    SessionArray.push(link);
    idHere.push(requestdata);
  }

  requestdata = JSON.stringify(requestdata);
  request.send(requestdata);
}

// Calling Checkbox source filter
$("#filterSources").click(function () {
  checkBoxValidation();
});

// Date Filter function
function dateFilter() {
  $("#cover-spin").show(0);
  d3.select(".cichart").selectAll("*").remove();
  d3.select(".legends").selectAll("*").remove();
  let sessionSDate = localStorage.getItem("startDate");
  let sessionEDate = localStorage.getItem("endDate");
  let sessionId = localStorage.getItem("id");
  var searchVal = document.getElementById("universalsearch").value;
  let typeOfSearch = localStorage.getItem("typeOfSearch");
  let case_id_available = localStorage.getItem("case_id");

  if (SessionArray.length !== 0) {
    document.getElementById("backBtn").style.display = "inline";
    document.getElementById("forwardBtn").style.display = "inline";
  }
  SessionPointer = SessionPointer + 1;

  if (SessionArray.length === SessionPointer) {
    document.getElementById("forwardBtn").style.display = "none";
  }

  if (sessionSDate && sessionEDate) {
    sessionSDate = sessionSDate.substr(0, 24);
    sessionEDate = sessionEDate.substr(0, 24);
  } else {
    console.log("no session date");
  }

  console.log(sessionSDate, sessionEDate, sessionId, " are sessions");
  if (sessionSDate && sessionEDate) {
    let link;
    var requestdata = {};
    if (sessionId != null && searchVal == "") {
      link = `${rootUrl}/getGraphForId`;
      requestdata = {
        startTime: sessionSDate,
        endTime: sessionEDate,
        id: Number(sessionId),
      };
    } else if (case_id_available) {
      link = `${rootUrl}/getGraphForCaseId`;
      requestdata = {
        startTime: sessionSDate,
        endTime: sessionEDate,
        caseId: case_id_available,
      };
    } else if (searchVal != "") {
      link = `${rootUrl}/getGraphForProperty`;
      requestdata = {
        startTime: sessionSDate,
        endTime: sessionEDate,
        search_for: typeOfSearch,
        search_value: searchVal,
      };
    }

    //Search val null condition to be added

    console.log(link);

    var request = new XMLHttpRequest();
    // Open a new connection, using the POST request on the URL endpoint
    request.open("POST", link);
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
        console.log(JSON.parse(this.response), "data here");
        getData(JSON.parse(this.response));
        populateCounter(JSON.parse(this.response));
      }
    };

    if (SessionPointer !== SessionArray.length) {
      SessionArray.splice(SessionPointer, 0, link);
      idHere.splice(SessionPointer, 0, requestdata);
    } else {
      SessionArray.push(link);
      idHere.push(requestdata);
    }

    requestdata = JSON.stringify(requestdata);
    request.send(requestdata);
  }
}

//Recent Time filters
$("#recentTimeFilter").click(function () {
  let sessionId = localStorage.getItem("id");
  let searchVal = document.getElementById("universalsearch").value;
  let case_id_available = localStorage.getItem("case_id");
  let typeOfSearch = localStorage.getItem("typeOfSearch");

  $("#cover-spin").show(0);
  d3.select(".cichart").selectAll("*").remove();
  d3.select(".legends").selectAll("*").remove();

  console.log(sessionId, "Time filter id");

  if (SessionArray.length !== 0) {
    document.getElementById("backBtn").style.display = "inline";
    document.getElementById("forwardBtn").style.display = "inline";
  }
  SessionPointer = SessionPointer + 1;

  if (SessionArray.length === SessionPointer) {
    document.getElementById("forwardBtn").style.display = "none";
  }

  var symbol = $("#timeFiltersymbol option:selected").val();
  var rangeVal = $("#inputTimeFilter").val();

  if (symbol !== "" && rangeVal !== "") {
    let link = `${rootUrl}/getRecentData`;

    console.log(link, "link");

    var request = new XMLHttpRequest();
    // Open a new connection, using the POST request on the URL endpoint
    request.open("POST", link);
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
        console.log(JSON.parse(this.response), "data here");
        getData(JSON.parse(this.response));
        populateCounter(JSON.parse(this.response));
      }
    };
    let objVal = {};

    if (sessionId !== null) {
      objVal = {
        id: Number(sessionId),
        type: symbol,
        range: Number(rangeVal),
      };
    } else if (searchVal !== "") {
      objVal = {
        search_for: typeOfSearch,
        search_value: searchVal,
        type: symbol,
        range: Number(rangeVal),
      };
    } else if (case_id_available) {
      objVal = {
        caseId: case_id_available,
        type: symbol,
        range: Number(rangeVal),
      };
    } else {
      alert("Please do any operations like double clicking a node / search ");
    }

    if (SessionPointer !== SessionArray.length) {
      SessionArray.splice(SessionPointer, 0, link);
      idHere.splice(SessionPointer, 0, objVal);
    } else {
      SessionArray.push(link);
      idHere.push(objVal);
    }

    var requestdata = JSON.stringify(objVal);

    request.send(requestdata);
  }
});

// User Process collapse api
function callCollapseApi(id, userUrl) {
  console.log(userUrl);
  $("#cover-spin").show(0);

  var request = new XMLHttpRequest();

  var newUrl = `${rootUrl}/collapseGraph`;

  // Open a new connection, using the POST request on the URL endpoint
  // request.open('POST', `${rootUrl}/collapse_user_process?graph=${graphVar}&id=${id}`, true)
  if (SessionArray.length !== 0) {
    document.getElementById("backBtn").style.display = "inline";
    document.getElementById("forwardBtn").style.display = "inline";
  }
  SessionPointer = SessionPointer + 1;

  if (SessionArray.length === SessionPointer) {
    document.getElementById("forwardBtn").style.display = "none";
  }

  request.open("POST", newUrl);

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
      var datalength = JSON.parse(this.response);
      if (datalength && datalength.edges && datalength.edges.length > 0) {
        getData(datalength);
        populateCounter(datalength);
      } else {
        datalength = JSON.parse(this.response);
        $("#exampleModal").modal("show");
        $("#errorDes").text("No data found");
      }
    }
  };

  let activeSourcesList = [];
  $("#semanticSource").prop("checked") && activeSourcesList.push("sepc");
  $("#watchgSource").prop("checked") && activeSourcesList.push("watchguard");
  $("#windowsSource").prop("checked") && activeSourcesList.push("windows");
  $("#sysmon").prop("checked") && activeSourcesList.push("sysmon");
  $("#msExchange").prop("checked") && activeSourcesList.push("msexchange");

  let sessionId = localStorage.getItem("id");
  let typeOfSearch = localStorage.getItem("typeOfSearch");
  let searchVal = document.getElementById("universalsearch").value;
  let caseIdVal = localStorage.getItem("case_id");
  let sessionSDate = localStorage.getItem("startDate");
  let sessionEDate = localStorage.getItem("endDate");
  let objVal = {};
  if (sessionSDate && sessionEDate && activeSourcesList.length > 0) {
    objVal = {
      id: id,
      collapse_by: userUrl,
      startTime: sessionSDate,
      endTime: sessionEDate,
      data_source_name: activeSourcesList.join(),
    };
  } else if (sessionSDate && sessionEDate && activeSourcesList.length === 0) {
    objVal = {
      id: id,
      collapse_by: userUrl,
      startTime: sessionSDate,
      endTime: sessionEDate,
    };
  } else if (!sessionSDate && !sessionEDate && activeSourcesList.length > 0) {
    objVal = {
      id: id,
      collapse_by: userUrl,
      data_source_name: activeSourcesList.join(),
    };
  } else {
    objVal = {
      id: id,
      collapse_by: userUrl,
    };
  }

  if (SessionPointer !== SessionArray.length) {
    SessionArray.splice(SessionPointer, 0, newUrl);
    idHere.splice(SessionPointer, 0, objVal);
  } else {
    SessionArray.push(newUrl);
    idHere.push(objVal);
  }

  const responseData = JSON.stringify(objVal);
  request.send(responseData);
}
