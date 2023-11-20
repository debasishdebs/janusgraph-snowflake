//Initializing all the variables
var width = 1024;
var height = 800;
var graphVar = "g";

var zoom = d3.zoom();

var clickedObjects = [];
var clickedIds = [];

var SessionArray = [];
var SessionPointer = -1;
var idHere = [];

var linkColorMap = {
  createdProcess: "#1f77b4",
  hasIP: "#aec7e8",
  clickdRel: "#ff7f0e",
  otherClickdRel: "#ffbb78",
  clicked: "#273b66",
  userInteracted: "#98df8a",
  assignedInternalIP: "#d62728",
  isEvent: "#ff9896",
  causedEvent: "#9467bd",
  runningProcess: "#c5b0d5",
  sentEmail: "#8c564b",
  receivedEmail: "#c49c94",
  processCommunicated: "#e377c2",
  sourceWithIP: "#f7b6d2",
  destinationWithIP: "#7f7f7f",
  senderBelongsTo: "#c7c7c7",
  receiverBelongsTo: "#bcbd22",
  withIP: "#dbdb8d",
  emailed: "#17becf",
  gotEmail: "#9edae5",
  resolved: "#244a3e",
  IPsCommunicated: "#e5b72d",
  downloadedBy: "#518561",
  downloadedFrom: "#ee7631",
  loggedIn: "#906cb2",
  downloadedOn: "#d8bdf2",
  childProcessOn: "#56ef78",
  childProcessCreated: "#f3565a",
  emailOriginatedFrom: "blue",
  emailSentTo: "violet",
  createdChildProcess: "#f3565a",
  clickedRel: "#f3565a",
  otherClickedRel: "#f3565a",
};

// image paths
var ipImage = "/images/ip-icon.png";
var pImage = "/images/host-icon.png";
var iconImage = "/images/icon.png";
var emailImage = "/images/Emails-icon.png";
var hostsImage = "/images/new/host-icon.png";
var processImage = "images/process.png";
var childProcessImage = "images/new/Child_process-icon.png";
var urlIcon = "images/new/URLs-icon.png";

// Date function
var dateValues = {
  startDate: moment(Date()).format("YYYY-MM-DD"),
  endDate: moment(Date()).format("YYYY-MM-DD"),
};

function datePickerValues(startDate, endDate) {
  localStorage.setItem("startDate", startDate.format("YYYY-MM-DD HH:mm:ss"));
  localStorage.setItem("endDate", endDate.format("YYYY-MM-DD HH:mm:ss"));
  dateValues.startDate = startDate.format("YYYY-MM-DD");
  dateValues.endDate = endDate.format("YYYY-MM-DD");
}

function checkSessionForDates() {
  let sessionStartDate = localStorage.getItem("startDate");
  let sessionEndDate = localStorage.getItem("endDate");
  if (sessionStartDate && sessionEndDate) {
    dateValues.startDate = moment(sessionStartDate).format("YYYY-MM-DD");
    dateValues.endDate = moment(sessionEndDate).format("YYYY-MM-DD");
    $("#config-demo").val(
      moment(sessionStartDate).format("MM[/]DD[/]YYYY") +
        " - " +
        moment(sessionEndDate).format("MM[/]DD[/]YYYY")
    );
  }
}

function getRequiredDates(dateType) {
  if (dateType === "startDate") {
    return (
      (localStorage.getItem("startDate") &&
        moment(localStorage.getItem("startDate")).format("MM[/]DD[/]YYYY")) ||
      moment().subtract(29, "days")
    );
  } else if (dateType === "endDate") {
    return (
      (localStorage.getItem("endDate") &&
        moment(localStorage.getItem("endDate")).format("MM[/]DD[/]YYYY")) ||
      moment()
    );
  }
}

// end of date function

// Populate on click results
function sideResults(d, typeOfGraph) {
  if (typeOfGraph === "network") {
    document.getElementById("sourcesId").innerHTML =
      d.dataSourceName || "  -  ";
    if (d.label === "") {
      document.getElementById("valueId").innerHTML = d.userName || "  -  ";
    } else if (d.label === "IP") {
      document.getElementById("valueId").innerHTML = d.ip || "  -  ";
    } else if (d.label === "URLs") {
      document.getElementById("urlCount").innerHTML = d.URL || "  -  ";
    } else {
      document.getElementById("valueId").innerHTML = d.fullFileName || "  -  ";
    }
  } else {
    document.getElementById("sourcesId").innerHTML =
      d.properties.dataSourceName || "  -  ";
    if (d.properties.userName) {
      document.getElementById("valueId").innerHTML =
        d.properties.userName || "  -  ";
    } else {
      document.getElementById("valueId").innerHTML = d.properties.ip || "  -  ";
    }
  }
}

// Populate image counter
function populateCounter(data) {
  var entityCounts = {
    emailCount: 0,
    userCount: 0,
    ipCount: 0,
    processCount: 0,
    hostCount: 0,
    urlCount: 0,
    childprocessCount: 0,
  };

  data.nodes.forEach(function (element) {
    if (element.label === "IP") {
      entityCounts.ipCount += 1;
    } else if (element.label === "user") {
      entityCounts.userCount += 1;
    } else if (element.label === "process") {
      entityCounts.processCount += 1;
    } else if (element.label === "email") {
      entityCounts.emailCount += 1;
    } else if (element.label === "hosts") {
      entityCounts.hostCount += 1;
    } else if (element.label === "URLs") {
      entityCounts.urlCount += 1;
    } else if (element.label === "childProcess") {
      entityCounts.childprocessCount += 1;
    }
  });
  document.getElementById("emailCount").innerHTML = entityCounts.emailCount;
  document.getElementById("userCount").innerHTML = entityCounts.userCount;
  document.getElementById("ipCount").innerHTML = entityCounts.ipCount;
  document.getElementById("processCount").innerHTML = entityCounts.processCount;
  document.getElementById("childprocessCount").innerHTML =
    entityCounts.childprocessCount;
  document.getElementById("hostCount").innerHTML = entityCounts.hostCount;
  document.getElementById("urlCount").innerHTML = entityCounts.urlCount;
}

// Back and forth button logic
document.getElementById("backBtn").onclick = function () {
  console.log(SessionArray, "backbtn Clicked");
  console.log(SessionPointer, idHere, "SessionPointer Clicked");

  SessionPointer = SessionPointer - 1;
  var previousUrl = SessionArray[SessionPointer];
  var previousId = idHere[SessionPointer];

  console.log(previousUrl, "previousUrl");

  if (SessionPointer === -1) {
    document.getElementById("backBtn").style.display = "none";
  }

  if (SessionArray.length !== SessionPointer) {
    document.getElementById("forwardBtn").style.display = "inline";
  }

  if (previousUrl) {
    $("#cover-spin").show(0);
    var request = new XMLHttpRequest();
    request.open("POST", previousUrl);
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
        getData(JSON.parse(this.response));
        populateCounter(JSON.parse(this.response));
      }
    };

    if (previousId === null) {
      obj1 = {
        search_for: localStorage.getItem("typeOfSearch"),
        search_value: searchVal,
        dedup: "true",
        hops: 1,
      };
    } else {
      obj1 = previousId;
    }
    // Send request
    const requestdata = JSON.stringify(obj1);
    request.send(requestdata);
  }
};

document.getElementById("forwardBtn").onclick = function () {
  console.log(idHere, "forwardBtn Clicked");

  console.log(SessionArray, "backbtn Clicked");
  console.log(SessionPointer, "SessionPointer Clicked");

  SessionPointer = SessionPointer + 1;
  var nextUrl = SessionArray[SessionPointer];
  var nextId = idHere[SessionPointer];

  console.log(nextUrl, "nextUrl");

  if (SessionPointer === SessionArray.length - 1) {
    document.getElementById("forwardBtn").style.display = "none";
  }

  if (SessionPointer !== 0) {
    document.getElementById("backBtn").style.display = "inline";
  }

  if (nextUrl) {
    $("#cover-spin").show(0);
    var request = new XMLHttpRequest();
    request.open("POST", nextUrl);
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
        getData(JSON.parse(this.response));
        populateCounter(JSON.parse(this.response));
      }
    };

    if (nextId === null) {
      obj1 = {
        search_for: typeOfSearch,
        search_value: searchVal,
        dedup: "true",
        hops: 1,
      };
    } else {
      obj1 = nextId;
    }
    // Send request
    const requestdata = JSON.stringify(obj1);
    request.send(requestdata);
  }
};

// getValue of type dropdown
function getval(value) {
  var typeset = $("#typeSource option:selected").val();
  localStorage.setItem("typeOfSearch", typeset);
}

$("#resetDate").on("click", function () {
  localStorage.setItem("startDate", null);
  localStorage.setItem("endDate", null);
});
