//Initializing all the variables

var width = 1024;
var height = 800;

// Date function
var dateValues = {
  startDate: moment(Date()).format("YYYY-MM-DD"),
  endDate: moment(Date()).format("YYYY-MM-DD"),
};

function datePickerValues(startDate, endDate) {
  localStorage.setItem("startDate", startDate);
  localStorage.setItem("endDate", endDate);
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
