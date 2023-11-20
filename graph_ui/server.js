// Importing/Require required modules
var express = require("express");
var app = express();
var path = require("path");
let router = express.Router();

var propertiesReader = require("properties-reader");
var properties = propertiesReader("application.properties");

console.log(`Properties file is ${properties}`);

const HOST = properties.get("ui.server.host");
const PORT = Number(properties.get("ui.server.port"));

console.log(`Starting on ${HOST}:${PORT}`);

// viewed at http://localhost:3001

//Adding routing
app.use(express.static(__dirname + "/public"));

app.get("/", function (req, res) {
  res.sendFile(path.join(__dirname + "/casemanagement.html"));
});

router.get("/dashboard", function (req, res) {
  res.sendFile(path.join(__dirname + "/index.html"));
});

app.use("/", router);
app.use(express.json());

// var uiPort = process.argv.slice(2, 3);

app.use(express.static("public"));
app.listen(PORT);

// To view on which port project is started
console.log(`Started on ${HOST}:${PORT}`);
