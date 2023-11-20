var contextMenuArray = [];

//Inital call
$(document).ready(function () {
  const case_id_param = localStorage.getItem("case_id");

  localStorage.setItem("typeOfSearch", "");
  localStorage.setItem("searchVal", "");

  $("#cover-spin").show(0);

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
  request.open("POST", `${rootUrl}/getGraphForCaseId`);

  // request headers
  request.setRequestHeader("Content-Type", "application/json");
  request.setRequestHeader("cache-control", "no-cache");
  request.setRequestHeader("Access-Control-Allow-Origin", "*");

  request.onload = function () {
    if (this.readyState == this.DONE) {
      $("#cover-spin").hide(0);
      console.log(JSON.parse(this.response), "data");
      getData(JSON.parse(this.response));
      populateCounter(JSON.parse(this.response));
    }
  };

  const objVal = {
    caseId: case_id_param,
    dedup: "true",
  };

  // Send request
  var requestdata = JSON.stringify(objVal);

  if (SessionPointer !== SessionArray.length) {
    SessionArray.splice(SessionPointer, 0, `${rootUrl}/getGraphForCaseId`);
    idHere.splice(SessionPointer, 0, objVal);
  } else {
    SessionArray.push(`${rootUrl}/getGraphForCaseId`);
    idHere.push(objVal);
  }
  request.send(requestdata);
});

var forceLink = d3
  .forceLink()
  .id(function (d) {
    return d.node_id;
  })
  .distance(function (d) {
    // return GetNodeDefaults(d).linkDistance;
    return 170;
  })
  .strength(1);

function startSimulation(nodes, links) {
  d3.select(".cichart").selectAll("*").remove();
  d3.select(".legends").selectAll("*").remove();

  document.getElementById("accordion").style.display = "inline";
  nodes.forEach(function (element) {
    if (element.label === "IP") {
      element.image = ipImage;
    } else if (element.label === "user") {
      element.image = iconImage;
    } else if (element.label === "process") {
      element.image = processImage;
    } else if (element.label === "email") {
      element.image = emailImage;
    } else if (element.label === "host") {
      element.image = hostsImage;
    } else if (element.label === "URLs") {
      element.image = urlIcon;
    } else if (element.label === "childProcess") {
      element.image = childProcessImage;
    }
  });

  function dragstart(d) {
    d.fixed = true;
  }

  function dragstarted(d) {
    console.log("drag started");
    if (!d3.event.active) simulation.alphaTarget(0.5).restart();
    d.fx = d.x;
    d.fy = d.y;
  }

  function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
  }

  function dragended(d) {
    console.log("drag ended");
    if (!d3.event.active) simulation.alphaTarget(0);
  }

  var simulation = d3
    .forceSimulation()
    .force("link", forceLink)
    // .force("link", d3.forceLink().id(function(d) { return d.node_id; }))
    .force(
      "charge",
      d3
        .forceManyBody()
        .strength(function (d, i) {
          var a = i == 0 ? -50 : -10;
          return a;
        })
        .distanceMin(100)
        .distanceMax(2000)
    )
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force(
      "collide",
      d3
        .forceCollide(function (d) {
          return 50;
        })
        .iterations(50)
    )
    .force("x", d3.forceX(width / 2))
    .force("y", d3.forceY(height / 2))
    .force("charge", d3.forceManyBody().strength(-30));

  let zoom = d3.zoom().on("zoom", zoomed);

  var svg = d3
    .select(".cichart")
    // Container class to make it responsive.
    .classed("svg-container", true)
    .append("svg")
    // Responsive SVG needs these 2 attributes and no width and height attr.
    .attr("preserveAspectRatio", "xMidYMid meet")
    .attr("viewBox", "0 100 1024 600")
    .call(
      d3.zoom().on("zoom", function () {
        svg.attr("transform", d3.event.transform);
      })
    )
    .on("dblclick.zoom", null)
    .append("g");

  d3.select("#zoom_in").on("click", function () {
    zoom.scaleBy(svg.transition().duration(750), 1.2);
  });
  d3.select("#zoom_out").on("click", function () {
    zoom.scaleBy(svg.transition().duration(750), 0.8);
  });

  function zoomed() {
    svg.attr("transform", d3.event.transform);
  }

  // here

  // Zoom slider
  // var zoom = d3.zoom()
  //     .scaleExtent([0, 10])
  //     .on("zoom", zoomed);

  // var slider = d3.select("#zoombtn").append("p").append("input")
  //     .datum({})
  //     .attr("type", "range")
  //     .attr("value", zoom.scaleExtent()[1])
  //     .attr("min", zoom.scaleExtent()[0])
  //     .attr("max", zoom.scaleExtent()[1])
  //     .attr("step", (zoom.scaleExtent()[1] - zoom.scaleExtent()[0]) / 100)
  //     .on("input", slided);

  // var svg = d3.select(".cichart")
  //     // Container class to make it responsive.
  //     .classed("svg-container", true)
  //     .append("svg")
  //     // Responsive SVG needs these 2 attributes and no width and height attr.
  //     .attr("preserveAspectRatio", "xMidYMid meet")
  //     .attr("viewBox", "0 100 1024 600")
  //     .call(zoom)
  //     .append("g");

  // function zoomed() {
  //     const currentTransform = d3.event.transform;
  //     svg.attr("transform", currentTransform);
  //     svg.property("value", currentTransform.k);
  // }

  // function slided(d) {
  //     zoom.scaleTo(svg, d3.select(this).property("value")/5);
  // }

  // here

  var svg2 = d3
    .select(".legends")
    .append("svg")
    .attr("width", "300px")
    .attr("height", "600px");

  var counter = {};

  links.forEach(function (obj) {
    var key = JSON.stringify(obj);
    counter[key] = (counter[key] || 0) + 1;
  });

  var finalArray = [];

  for (var key in counter) {
    var tempkey =
      key.substring(0, key.length - 1) + ',"value":' + counter[key] + "}";
    finalArray.push(tempkey);
  }
  finalArray.forEach(function (d, i, array) {
    array[i] = JSON.parse(d);
  });

  var lookup = {};
  var linkLabels = [];
  var linkLabelColorMap = {};
  finalArray.forEach(function (l) {
    var label = l.label;
    if (!(label in lookup)) {
      lookup[label] = 1;
      linkLabels.push(label);
      linkLabelColorMap[label] = linkColorMap[label];
    }
  });

  // Build the arrow.
  console.log(linkLabels);

  svg
    .append("svg:defs")
    .selectAll("marker")
    .data(linkLabels) // Different link/path types can be defined here
    .enter()
    .append("svg:marker") // This section adds in the arrows
    .attr("id", String)
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 40)
    .attr("refY", -4)
    .attr("markerWidth", 10)
    .attr("markerHeight", 10)
    .attr("orient", "auto")
    .append("svg:path")
    .attr("d", "M0,-5L10,0L0,5")
    .attr("stroke-width", "userSpaceOnUse")
    .style("fill", function (l) {
      return linkLabelColorMap[l];
    });

  var link = svg
    .append("g")
    .attr("class", "links")
    .selectAll("line")
    .data(finalArray)
    // .enter().append("line") // For Straight lines
    .enter()
    .append("path") // For curvy lines
    .attr("marker-end", function (l) {
      return "url(#" + l.label + ")";
    })
    .attr("stroke", function (d) {
      return linkLabelColorMap[d.label];
    })
    // .style("stroke-dasharray", ("6, 6"))  //For Dahsed links
    .style("fill", "none");
  // Manage stroke width / link width

  // .attr("stroke-width" , 1)
  // .attr("stroke-width", function (d) {
  //     if (Math.sqrt(d.value) < 15)
  //         return Math.sqrt(Math.sqrt(d.value))
  //     else
  //         return Math.sqrt(Math.sqrt(225))
  // });

  link.append("title").text(function (l) {
    return l.label;
  });

  // Add the Legend menu
  var legend = svg2
    .append("g")
    .attr("class", "legend")
    // .attr("x",0)
    // .attr("y", 25)
    .attr("height", 100)
    .attr("width", 100);

  legend
    .selectAll("g")
    .data(linkLabels)
    .enter()
    .append("g")
    .each(function (l, i) {
      var g = d3.select(this);
      g.append("rect")
        .attr("x", 30)
        .attr("y", 390 + i * 20)
        .attr("width", 10)
        .attr("height", 10)
        .style("fill", function () {
          // Add the colours dynamically
          return linkLabelColorMap[l];
        });

      g.append("text")
        .attr("x", 50) // space legend
        .attr("y", 400 + i * 20)
        .attr("class", "legend") // style the legend
        .style("fill", function () {
          // Add the colours dynamically
          return linkLabelColorMap[l];
        })
        .text(l);
    });

  var node = svg
    .append("g")
    .attr("class", "nodes")
    .selectAll("g")
    .data(nodes)
    .enter()
    .append("g");

  // var circles = node.append("circle")
  //     .attr("fill", "white")
  //     .attr("class", "foo")
  //     .attr('r', 30);

  var circles = node
    .append("circle")
    .style("fill", function (d) {
      if (d.severity === "red") {
        return "#FFE5E5";
      } else {
        return "white";
      }
    })
    // .style("opacity", function (d) {
    //     if (d.severity === 'red') {
    //         return 0.1 ;
    //     }
    // })
    .attr("class", "foo")
    .attr("r", 30);

  var nodeImage = node
    .append("image")
    .attr("xlink:href", (d) => d.image)
    .attr("height", "50")
    .attr("width", "50")
    .attr("x", -25)
    .attr("y", -25)
    .call(
      d3
        .drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended)
    );

  var lables = node
    .append("text")
    .text(function (d) {
      if (d.label == "user") {
        return d.userName;
      } else if (d.label == "IP") {
        return d.ip;
      } else if (d.label == "email") {
        return d.emailSubject;
      } else if (d.label == "host") {
        return d.hostname;
      } else if (d.label == "URLs") {
        return d.URL;
      } else if (d.label == "childProcess") {
        return d.fileName;
      } else {
        return d.fileName;
      }
    })
    .attr("x", -40)
    .attr("y", 40)
    .style("font-size", "13px");

  node.append("title").text(function (d) {
    return d.lable;
  });

  simulation.nodes(nodes).on("tick", ticked);
  simulation.force("link").links(finalArray);

  node.on("mouseover", function (d) {
    link.style("stroke", function (l) {
      if (d === l.source || d === l.target) return "grey";
      else return linkLabelColorMap[d.label];
    });
  });
  node.on("mouseout", function () {
    link.style("stroke", function (d) {
      return linkLabelColorMap[d.label];
    });
    svg.attr("stroke", function (l) {
      return linkLabelColorMap[l];
    });
  });

  node.on("contextmenu", function (d, i, nodes, finalArray) {
    rightClicknode(d, i, nodes, finalArray);
  });

  nodeImage.on("dblclick", function (d) {
    doubleClicknode(d);
  });

  svg.on("mousedown", function () {
    d3.select("#contextMenuNode").style("display", "none");
  });

  nodeImage.on("click", function (n) {
    if (d3.event.ctrlKey) {
      clickedObjects.push(n);
      clickedIds.push(n.node_id);

      console.log(clickedObjects, clickedIds, "clicked objects");

      circles.style("stroke", function (d) {
        if (clickedIds.includes(d.node_id)) return "#c83531";
      });
      circles.style("stroke-dasharray", function (d) {
        if (clickedIds.includes(d.node_id)) return 5;
      });
      circles.style("stroke-width", function (d) {
        if (clickedIds.includes(d.node_id)) return 3;
      });
    } else {
      // callOnClickAPI(n.node_id, n);
      // stasticalAPi(n.node_id)
      // profilerData(n)
      clickedObjects = [];
      clickedIds = [];
      circles.style("stroke", function (d) {
        if (d.node_id == n.node_id) return "#4f4f5f";
        else return "white";
      });
      circles.style("stroke-dasharray", function (d) {
        if (d.node_id == n.node_id) return 5;
        else return 0;
      });
      circles.style("stroke-width", function (d) {
        if (d.node_id == n.node_id) return 3;
        else return 0;
      });
      sideResults(n, "network");
    }
  });

  function rightClicknode(d, i, nodes, links) {
    var view = d3.select("#contextMenuNode");

    if (d.label === "IP") {
      view.html(`<ul class="contextmenu">
    
            <li><a>Expand <i class="arrow right-arrow"></i></a>
              <ul class="submenu">
                <li><a>All</a>
                    <ul class="submenusub">
                        <li onclick="callExpandApi(${d.node_id} , 'all' , 1); return false;" ><a>1</a></li>
                        <li onclick="callExpandApi(${d.node_id} , 'all' , 2); return false;" ><a>2</a></li>
                        <li onclick="callExpandApi(${d.node_id} , 'all' , 3); return false;" ><a>3</a></li>
                    </ul>
                </li>
    
                <li><a>Has IP</a>
                    <ul class="submenusub">
                        <li onclick="callExpandApi(${d.node_id} , 'hasIP' , 1); return false;"><a>1</a></li>
                        <li onclick="callExpandApi(${d.node_id} , 'hasIP' , 2); return false;"><a>2</a></li>
                        <li onclick="callExpandApi(${d.node_id} , 'hasIP' , 3);return false;"><a>3</a></li>
                    </ul>
                </li>
    
                <li><a>IP's Communicated</a>
                    <ul class="submenusub">
                        <li onclick="callExpandApi(${d.node_id} , 'IPsCommunicated' , 1); return false;" ><a>1</a></li>
                        <li onclick="callExpandApi(${d.node_id} , 'IPsCommunicated' , 2); return false;" ><a>2</a></li>
                        <li onclick="callExpandApi(${d.node_id} , 'IPsCommunicated' , 3); return false;" ><a>3</a></li>
                    </ul>
                </li>
    
                <li><a>Process Communicated</a>
                    <ul class="submenusub">
                        <li  onclick="callExpandApi(${d.node_id} , 'processCommunicated' , 1); return false;"><a>1</a></li>
                        <li  onclick="callExpandApi(${d.node_id} , 'processCommunicated' , 2); return false;"><a>2</a></li>
                        <li  onclick="callExpandApi(${d.node_id} , 'processCommunicated' , 3); return false;"><a>3</a></li>
                    </ul>
                </li>

                <li><a>Downloaded On</a>
                    <ul class="submenusub">
                        <li  onclick="callExpandApi(${d.node_id} , 'downloadedOn' , 1); return false;"><a>1</a></li>
                        <li  onclick="callExpandApi(${d.node_id} , 'downloadedOn' , 2); return false;"><a>2</a></li>
                        <li  onclick="callExpandApi(${d.node_id} , 'downloadedOn' , 3); return false;"><a>3</a></li>
                    </ul>
                </li>

              </ul>
    
            </li>
    
            <li><a>Collapse <i class="arrow right-arrow"></i></a>
                <ul class="submenu">
                    <li style="margin-top:70px" onclick="callCollapseApi(${d.node_id} , 'ip_user'); return false;"><a>Users who used IP</a></li>
                </ul>
            </li>
    
          </ul>`);
    } else if (d.label === "process" || d.label === "childProcess") {
      view.html(`<ul class="contextmenu">
    
            <li><a>Expand <i class="arrow right-arrow"></i></a>
              <ul class="submenu">
                <li><a>All</a>
                    <ul class="submenusub">
                        <li onclick="callExpandApi(${d.node_id} , 'all' , 1); return false;" ><a>1</a></li>
                        <li onclick="callExpandApi(${d.node_id} , 'all' , 2); return false;" ><a>2</a></li>
                        <li onclick="callExpandApi(${d.node_id} , 'all' , 3); return false;" ><a>3</a></li>
                    </ul>
                </li>
    
                <li><a>Created Process</a>
                    <ul class="submenusub">
                        <li onclick="callExpandApi(${d.node_id} , 'createdProcess' , 1); return false;" ><a>1</a></li>
                        <li onclick="callExpandApi(${d.node_id} , 'createdProcess' , 2); return false;" ><a>2</a></li>
                        <li onclick="callExpandApi(${d.node_id} , 'createdProcess' , 3); return false;" ><a>3</a></li>
                    </ul>
                </li>
    
                <li><a>Running Process</a>
                    <ul class="submenusub">
                        <li  onclick="callExpandApi(${d.node_id} , 'runningProcess' , 1); return false;"><a>1</a></li>
                        <li  onclick="callExpandApi(${d.node_id} , 'runningProcess' , 2); return false;"><a>2</a></li>
                        <li  onclick="callExpandApi(${d.node_id} , 'runningProcess' , 3); return false;"><a>3</a></li>
                    </ul>
                </li>
    
                <li><a>Process Communicated</a>
                    <ul class="submenusub">
                        <li  onclick="callExpandApi(${d.node_id} , 'processCommunicated' , 1); return false;"><a>1</a></li>
                        <li  onclick="callExpandApi(${d.node_id} , 'processCommunicated' , 2); return false;"><a>2</a></li>
                        <li  onclick="callExpandApi(${d.node_id} , 'processCommunicated' , 3); return false;"><a>3</a></li>
                    </ul>
                </li>
              </ul>
    
            </li>
    
            <li><a>Collapse <i class="arrow right-arrow"></i></a>
                <ul class="submenu">
                    <li onclick="callCollapseApi(${d.node_id} , 'process_downloaded_on'); return false;"><a>Where process downloaded on</a></li>
                    <li onclick="callCollapseApi(${d.node_id} , 'collapse_process_communicated'); return false;"><a>Process-IP-Communicated</a></li>
                    <li onclick="callCollapseApi(${d.node_id} , 'process_ip'); return false;"><a>Where process communicated</a></li>
                    <li onclick="callCollapseApi({
                        "id": ${d.node_id},
                        "collapse_by": "user_process_user"
                      },'user_process_user'); return false;"><a>Others users with same process</a></li>
                    <li onclick="callCollapseApi(${d.node_id} , 'process_user'); return false;"><a>Who else downloaded process</a></li>
                </ul>
            </li>
          </ul>`);
    } else if (d.label === "URLs") {
      view.html(`<ul class="contextmenu">
    
            <li><a>Expand <i class="arrow right-arrow"></i></a>
              <ul class="submenu">
                <li><a>All</a>
                    <ul class="submenusub">
                        <li onclick="callExpandApi(${d.node_id} , 'all' , 1); return false;" ><a>1</a></li>
                        <li onclick="callExpandApi(${d.node_id} , 'all' , 2); return false;" ><a>2</a></li>
                        <li onclick="callExpandApi(${d.node_id} , 'all' , 3); return false;" ><a>3</a></li>
                    </ul>
                </li>
    
                <li><a>Clicked</a>
                    <ul class="submenusub">
                        <li onclick="callExpandApi(${d.node_id} , 'clicked' , 1); return false;" ><a>1</a></li>
                        <li onclick="callExpandApi(${d.node_id} , 'clicked' , 2); return false;" ><a>2</a></li>
                        <li onclick="callExpandApi(${d.node_id} , 'clicked' , 3); return false;" ><a>3</a></li>
                    </ul>
                </li>
    
                <li><a>Downloaded From</a>
                    <ul class="submenusub">
                        <li  onclick="callExpandApi(${d.node_id} , 'downloadedFrom' , 1); return false;"><a>1</a></li>
                        <li  onclick="callExpandApi(${d.node_id} , 'downloadedFrom' , 2); return false;"><a>2</a></li>
                        <li  onclick="callExpandApi(${d.node_id} , 'downloadedFrom' , 3); return false;"><a>3</a></li>
                    </ul>
                </li>
              </ul>
            </li>
    
            <li><a>Collapse <i class="arrow right-arrow"></i></a>
                <ul class="submenu">
                    <li onclick="callCollapseApi(${d.node_id} , 'collapse_user_clicked_url'); return false;"><a>URLs user visited</a></li>
                    <li onclick="callCollapseApi(${d.node_id}, 'user_email_user'); return false;"><a>Emails recieved</a></li>
                    <li onclick="callCollapseApi(${d.node_id} , 'user_URL_user'); return false;"><a>Other users clicking same URL</a></li>
                </ul>
            </li>
    
          </ul>`);
    } else if (d.label === "hosts") {
      view.html(`<ul class="contextmenu">
    
            <li><a>Expand <i class="arrow right-arrow"></i></a>
              <ul class="submenu">
                <li><a>All</a>
                    <ul class="submenusub">
                        <li onclick="callExpandApi(${d.node_id} , 'all' , 1); return false;" ><a>1</a></li>
                        <li onclick="callExpandApi(${d.node_id} , 'all' , 2); return false;" ><a>2</a></li>
                        <li onclick="callExpandApi(${d.node_id} , 'all' , 3); return false;" ><a>3</a></li>
                    </ul>
                </li>
    
                <li><a>Logged In</a>
                    <ul class="submenusub">
                        <li onclick="callExpandApi(${d.node_id} , 'loggedIn' , 1); return false;" ><a>1</a></li>
                        <li onclick="callExpandApi(${d.node_id} , 'loggedIn' , 2); return false;" ><a>2</a></li>
                        <li onclick="callExpandApi(${d.node_id} , 'loggedIn' , 3); return false;" ><a>3</a></li>
                    </ul>
                </li>

                <li><a>Running Process</a>
                    <ul class="submenusub">
                        <li  onclick="callExpandApi(${d.node_id} , 'runningProcess' , 1); return false;"><a>1</a></li>
                        <li  onclick="callExpandApi(${d.node_id} , 'runningProcess' , 2); return false;"><a>2</a></li>
                        <li  onclick="callExpandApi(${d.node_id} , 'runningProcess' , 3); return false;"><a>3</a></li>
                    </ul>
                </li>
    
                <li><a>Downloaded On</a>
                    <ul class="submenusub">
                        <li  onclick="callExpandApi(${d.node_id} , 'downloadedOn' , 1); return false;"><a>1</a></li>
                        <li  onclick="callExpandApi(${d.node_id} , 'downloadedOn' , 2); return false;"><a>2</a></li>
                        <li  onclick="callExpandApi(${d.node_id} , 'downloadedOn' , 3); return false;"><a>3</a></li>
                    </ul>
                </li>
              </ul>
            </li>
    
            <li><a>Collapse <i class="arrow right-arrow"></i></a>
                <ul class="submenu">
                     <li style="margin-top:70px" onclick="callCollapseApi(${d.node_id} , 'collapse_host_user'); return false;"><a>Users who logged into this Host</a></li>
                </ul>
            </li>
    
          </ul>`);
    } else if (d.label === "user") {
      view.html(`<ul class="contextmenu">
  
            <li><a>Expand <i class="arrow right-arrow"></i></a>
              <ul class="submenu">
                <li><a>All</a>
                    <ul class="submenusub">
                        <li onclick="callExpandApi(${d.node_id} , 'all' , 1); return false;" ><a>1</a></li>
                        <li onclick="callExpandApi(${d.node_id} , 'all' , 2); return false;" ><a>2</a></li>
                        <li onclick="callExpandApi(${d.node_id} , 'all' , 3); return false;" ><a>3</a></li>
                    </ul>
                </li>
    
                <li><a>Has IP</a>
                    <ul class="submenusub">
                        <li onclick="callExpandApi(${d.node_id} , 'hasIP' , 1); return false;"><a>1</a></li>
                        <li onclick="callExpandApi(${d.node_id} , 'hasIP' , 2); return false;"><a>2</a></li>
                        <li onclick="callExpandApi(${d.node_id} , 'hasIP' , 3);return false;"><a>3</a></li>
                    </ul>
                </li>

                <li><a>Logged In</a>
                    <ul class="submenusub">
                        <li onclick="callExpandApi(${d.node_id} , 'loggedIn' , 1); return false;" ><a>1</a></li>
                        <li onclick="callExpandApi(${d.node_id} , 'loggedIn' , 2); return false;" ><a>2</a></li>
                        <li onclick="callExpandApi(${d.node_id} , 'loggedIn' , 3); return false;" ><a>3</a></li>
                    </ul>
                </li>


                <li><a>Sent Email</a>
                   <ul class="submenusub">
                        <li  onclick="callExpandApi(${d.node_id} , 'sentEmail' , 1); return false;"><a>1</a></li>
                        <li  onclick="callExpandApi(${d.node_id} , 'sentEmail' , 2); return false;"><a>2</a></li>
                        <li  onclick="callExpandApi(${d.node_id} , 'sentEmail' , 3); return false;"><a>3</a></li>
                    </ul>
                </li>
    
                <li><a>Received Email</a>
                    <ul class="submenusub">
                        <li  onclick="callExpandApi(${d.node_id} , 'receivedEmail' , 1); return false;"><a>1</a></li>
                        <li  onclick="callExpandApi(${d.node_id} , 'receivedEmail' , 2); return false;"><a>2</a></li>
                        <li  onclick="callExpandApi(${d.node_id} , 'receivedEmail' , 3); return false;"><a>3</a></li>
                    </ul>
                </li>

                <li><a>Created Process</a>
                    <ul class="submenusub">
                        <li  onclick="callExpandApi(${d.node_id} , 'createdProcess' , 1); return false;"><a>1</a></li>
                        <li  onclick="callExpandApi(${d.node_id} , 'createdProcess' , 2); return false;"><a>2</a></li>
                        <li  onclick="callExpandApi(${d.node_id} , 'createdProcess' , 3); return false;"><a>3</a></li>
                    </ul>
                </li>

              </ul>
            </li>
    
            <li><a>Collapse <i class="arrow right-arrow"></i></a>
                <ul class="submenu">
                    <li onclick="callCollapseApi(${d.node_id} , 'collapse_user_clicked_url'); return false;"><a>URLs user visited</a></li>
                    <li onclick="callCollapseApi(${d.node_id} , 'user_process_user'); return false;"><a>Others users with same process</a></li>
                    <li onclick="callCollapseApi(${d.node_id} , 'user_process'); return false;"><a>Downloaded processes</a></li>
                    <li onclick="callCollapseApi(${d.node_id}, 'user_email_user'); return false;"><a>Emails recieved</a></li>
                    <li onclick="callCollapseApi(${d.node_id} , 'user_URL_user'); return false;"><a>Other users clicking same URL</a></li>
                    <li onclick="callCollapseApi(${d.node_id} , 'user_touched_host'); return false;"><a>Logged into</a></li>
                </ul>
            </li>
    
          </ul>`);
    } else if (d.label === "email") {
      view.html(`<ul class="contextmenu">
    
            <li><a>Expand <i class="arrow right-arrow"></i></a>
              <ul class="submenu">
                <li><a>All</a>
                    <ul class="submenusub">
                        <li onclick="callExpandApi(${d.node_id} , 'all' , 1); return false;" ><a>1</a></li>
                        <li onclick="callExpandApi(${d.node_id} , 'all' , 2); return false;" ><a>2</a></li>
                        <li onclick="callExpandApi(${d.node_id} , 'all' , 3); return false;" ><a>3</a></li>
                    </ul>
                </li>
    
                <li><a>Sent Email</a>
                   <ul class="submenusub">
                        <li  onclick="callExpandApi(${d.node_id} , 'sentEmail' , 1); return false;"><a>1</a></li>
                        <li  onclick="callExpandApi(${d.node_id} , 'sentEmail' , 2); return false;"><a>2</a></li>
                        <li  onclick="callExpandApi(${d.node_id} , 'sentEmail' , 3); return false;"><a>3</a></li>
                    </ul>
                </li>
    
                <li><a>Received Email</a>
                    <ul class="submenusub">
                        <li  onclick="callExpandApi(${d.node_id} , 'receivedEmail' , 1); return false;"><a>1</a></li>
                        <li  onclick="callExpandApi(${d.node_id} , 'receivedEmail' , 2); return false;"><a>2</a></li>
                        <li  onclick="callExpandApi(${d.node_id} , 'receivedEmail' , 3); return false;"><a>3</a></li>
                    </ul>
                </li>

              </ul>
            </li>
    
            <li><a>Collapse <i class="arrow right-arrow"></i></a>
                <ul class="submenu">
                    <li onclick="callCollapseApi(${d.node_id} , 'collapse_user_clicked_url'); return false;"><a>URLs user visited</a></li>          
                </ul>
            </li>
          </ul>`);
    }

    $(document).contextmenu(function (e) {
      //Display contextmenu:
      $(".contextmenu")
        .css({
          //   "left": posLeft,
          //   "top": posTop
        })
        .show();
      //Prevent browser default contextmenu.
      return false;
    });
    //Hide contextmenu:
    $(document).click(function () {
      $(".contextmenu").hide();
    });

    // console.log('right clicked!!' + d.userName + ":" + d.label);

    d3.select("#contextMenuNode")
      .style("position", "absolute")
      .style("left", d3.event.pageX + "px")
      .style("top", d3.event.pageY + "px")
      .style("display", "inline");
    d3.event.preventDefault();
  }

  function doubleClicknode(d) {
    d3.select(".cichart").selectAll("*").remove();
    d3.select(".legends").selectAll("*").remove();
    getDrilldowndata(d);
  }

  // add the curvy lines
  function ticked() {
    link.attr("d", function (d) {
      var dx = d.target.x - d.source.x,
        dy = d.target.y - d.source.y,
        dr = Math.sqrt(dx * dx + dy * dy);
      return (
        "M" +
        d.source.x +
        "," +
        d.source.y +
        "A" +
        dr +
        "," +
        dr +
        " 0 0,1 " +
        d.target.x +
        "," +
        d.target.y
      );
    });

    //  for straight link
    // link
    //     .attr("x1", function (d) { return d.source.x; })
    //     .attr("y1", function (d) { return d.source.y; })
    //     .attr("x2", function (d) { return d.target.x; })
    //     .attr("y2", function (d) { return d.target.y; });

    node.attr("transform", function (d) {
      return "translate(" + d.x + "," + d.y + ")";
    });
  }
}

function getData(jsondata) {
  console.log(jsondata, "jsondata");
  startSimulation(jsondata.nodes, jsondata.edges);
}
