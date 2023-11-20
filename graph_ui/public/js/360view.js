// Calling Expand API here
function callExpandApi(id, selection, hops) {
  $("#cover-spin").show(0);
  var request = new XMLHttpRequest();
  // Open a new connection, using the POST request on the URL endpoint
  request.open("POST", `${rootUrl}/getGraphForId`);

  // request headers
  request.setRequestHeader("Content-Type", "application/json");
  request.setRequestHeader("cache-control", "no-cache");
  request.setRequestHeader("Access-Control-Allow-Origin", "*");

  if (SessionArray.length !== 0) {
    document.getElementById("backBtn").style.display = "inline";
    document.getElementById("forwardBtn").style.display = "inline";
  }
  SessionPointer = SessionPointer + 1;

  if (SessionArray.length === SessionPointer) {
    document.getElementById("forwardBtn").style.display = "none";
  }

  request.onload = function () {
    if (this.readyState == this.DONE) {
      $("#cover-spin").hide(0);
      var datalength = JSON.parse(this.response);
      if (datalength.edges.length > 0) {
        console.log(JSON.parse(this.response), "data here");
        getData(JSON.parse(this.response));
        populateCounter(JSON.parse(this.response));
      } else {
        $("#exampleModal").modal("show");
        $("#errorDes").text("No data found");
      }
    }
  };
  let selectedData = {};
  let typeOfSearch = localStorage.getItem("typeOfSearch");
  let searchVal = document.getElementById("universalsearch").value;
  let sessionSDate = localStorage.getItem("startDate");
  let sessionEDate = localStorage.getItem("endDate");
  if (selection === "all") {
    if (sessionSDate && sessionEDate) {
      if (searchVal != "") {
        selectedData = {
          search_value: searchVal,
          search_for: typeOfSearch,
          dedup: "true",
          hops: hops,
          startTime: sessionSDate,
          endTime: sessionEDate,
        };
      } else {
        selectedData = {
          id: id,
          dedup: "true",
          hops: hops,
          startTime: sessionSDate,
          endTime: sessionEDate,
        };
      }
    }
  } else {
    if (sessionSDate && sessionEDate) {
      if (searchVal != "") {
        selectedData = {
          search_value: searchVal,
          search_for: typeOfSearch,
          dedup: "true",
          hops: hops,
          startTime: sessionSDate,
          endTime: sessionEDate,
          selection: selection,
        };
      } else {
        selectedData = {
          id: id,
          dedup: "true",
          hops: hops,
          startTime: sessionSDate,
          endTime: sessionEDate,
          selection: selection,
        };
      }
    } else {
      selectedData = {
        id: id,
        dedup: "true",
        hops: hops,
        selection: selection,
      };
    }
  }

  if (SessionPointer !== SessionArray.length) {
    SessionArray.splice(SessionPointer, 0, `${rootUrl}/getGraphForId`);
    idHere.splice(SessionPointer, 0, selectedData);
  } else {
    SessionArray.push(`${rootUrl}/getGraphForId`);
    idHere.push(selectedData);
  }

  // Send request
  var requestdata = JSON.stringify(selectedData);
  // request.send(requestdata);
  request.send(requestdata);
}
