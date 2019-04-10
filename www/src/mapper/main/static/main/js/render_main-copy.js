$(function () {
  // This code uses version 3 of d3js
  // Set margins and sizes
  const mapperEndpoint = 'api/mapper';
  var margin = {
    top: 20,
    bottom: 50,
    right: 30,
    left: 50
  }

  var width = 960 - margin.left - margin.right
  var height = 550 - margin.top - margin.bottom


  //Load Color Scale
  var c10 = d3.scale.category10()
  var sentimentColor = {
    "positive": "#3AE71E",
    "negative": "red",
    "neutral": "blue"
  }

  //Create an SVG element and append it to the DOM


  var mSvg = d3.select(".mgraph")
    .append("svg")
    .classed("svg-content-responsive", true)
    .attr("preserveAspectRatio", "xMinYMin meet")
    .attr("viewBox", "0 0 " + (height + margin.top + margin.bottom) + " " + (width + margin.left + margin.right))
    .call(d3.behavior.zoom().on("zoom", function () {
      mSvg.attr("transform", "translate(" + d3.event.translate + ")" + " scale(" + d3.event.scale + ")")
    }))
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")")

  //---------------------------------------------------Functions-----------------------------------
  function render(nodes, links) {
    var radiusFunc = node => {
      node.radius = 25
      return 25 //node.score / 5 > 10 ? node.score / 5 : 20
    }

    d3.select(".graph").select('svg').remove()
    let canvas = d3.select(".graph")
      .append("svg")
      .attr("width", width)
      .attr("height", height)
      .classed("svg-content-responsive", true)
      .attr("preserveAspectRatio", "xMinYMin meet")
      .attr("viewBox", "0 0 " + (height + margin.top + margin.bottom) + " " + (width + margin.left + margin.right))

    canvas = canvas
      .call(d3.behavior.zoom().on("zoom", function () {
        canvas.attr("transform", "translate(" + d3.event.translate + ")" + " scale(" + d3.event.scale + ")")
      }))

      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
  //Add links to SVG
  canvas.append("defs").append("marker")
  .attr("id", "arrow")
  .attr("viewBox", "0 -5 10 10")
  .attr('refX', 8)
  .attr('refY', 0)
  .attr("markerWidth", 6)
  .attr("markerHeight", 6)
  .attr("orient", "auto")
  .append("path")
  .attr("d", "M0,-5L10,0L0,5");
    //Create Force Layout
    var force = d3.layout.force()
      .size([width, height])
      .nodes(nodes)
      .links(links)
      .on("tick", tick)
      .gravity(0.5)
      .charge(-5000)
      .linkDistance(200)

  

    let edges = canvas.append('g').selectAll("path")
      .data(force.links())

    edges.exit().remove()

    path = edges.enter().append("path")
      .attr("class", "link")
      .style("stroke", "#ccc")
      .attr('marker-end', (d) => "url(#arrow)")
      .style("stroke-width", 2)


    //Add nodes to SVG
    let node = canvas.append('g').selectAll("circle")
      .data(nodes)

    node.exit()
      .transition().duration(1000)
      .attr('r', 0).remove()

    node.enter().append("g")
      .attr("class", "node")
      .call(force.drag)

    //Add circles to each node
    node.append("circle")
      .attr("r", radiusFunc)
      .attr("fill", d => {
        if (d.type == "sentiment") {
          return sentimentColor[d.name]
        } else if (d.type == "author") {
          return "orange"
        } else if (d.type == "comment") {
          if (d.parent_id == d.article_id) {
            return "pink"
          }
          return "#5EDA9E"
        } else {
          return "cyan"
        }
      }).on('click', articleClick)

    node.append("title")
      .text(d => {
        if (d.type == "comment") return d.body
        else if (d.type == "article") return d.title
        else return d.name
      })
    node.append('text')
      .attr("text-anchor", "middle")
      .attr("pointer-events", "none")
      .text(d => getNodeText(d))

    //Start the force layout calculation
    force.start()

    function tick() {
      path.attr("d", linkArc);
      node.attr("transform", transform);
    }

    function transform(d) {
      return "translate(" + d.x + "," + d.y + ")";
    }
  }

  function addPropertyControl(nodes) {
    let properties = null
    for (var i = 0; i < nodes.length; i++) {
      if (nodes[i].type == "comment") {
        properties = Object.getOwnPropertyNames(nodes[i])
        break;
      }
    }

    var filtersEnter = d3.select('.dropdown-menu').selectAll('button')
      .data(properties).enter();

    filtersEnter.append('button')
      .attr('text-overflow', 'ellipsis')
      .attr('white-space', 'nowrap')
      .attr('class', 'dropdown-item')
      .attr('overflow', 'hidden')
      .attr('width', '200px')
      .text(d => d)
  }

  function getNodeText(node) {
    if (node.type == "author") return node["name"]
    else if (node.type == "sentiment") return node["name"]
    else return node.type
  }

  function articleClick(node) {
    if (node.type == 'article') {
      d3.select('.legend')
        .text(node.title)

      $.ajax({
        url: 'api/nodes/article/' + node.id,
        type: 'GET',
        success: function (json) {
          addPropertyControl(json.nodes)

          const nodes = json.nodes,
            links = json.links
          render(nodes, links)
        },
        error: function (xhr, errormsg, error) {
          console.log(error)
        }
      });
    }
  }

  loadGraph()

  function loadGraph() {
    $.ajax({
      url: 'api/nodes/article',
      type: 'GET',
      success: function (json) {
        if (!('links' in json))
          json['links'] = []

        const nodes = json.nodes,
          links = json.links
        console.log("Main")
        console.log(json)
        render(nodes, links)
      },
      error: function (xhr, errormsg, error) {}
    });
  }

  function loadMapperGraph(url = mapperEndpoint) {
    $.ajax({
      url: url,
      type: 'GET',
      success: function (json) {
        if (!('links' in json))
          json['links'] = []

        const nodes = json.nodes,
          links = json.links
        console.log("Mapper")
        console.log(nodes)
        renderMapper(nodes, links)
      },
      error: function (xhr, errormsg, error) {
        console.log(error)
      }
    });

    function renderMapper(nodes, links) {
      var radiusFunc = node => {
        node.radius = 25
        return 25 //node.score / 5 > 10 ? node.score / 5 : 20
      }

      d3.select(".mgraph").select('svg').remove()
      let canvas = d3.select(".mgraph")
        .append("svg")
        .classed("svg-content-responsive", true)
        .attr("preserveAspectRatio", "xMinYMin meet")
        .attr("viewBox", "0 0 " + (height + margin.top + margin.bottom) + " " + (width + margin.left + margin.right))

      canvas = canvas
        .call(d3.behavior.zoom().on("zoom", function () {
          canvas.attr("transform", "translate(" + d3.event.translate + ")" + " scale(" + d3.event.scale + ")")
        }))
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")

      //Create Force Layout
      var force = d3.layout.force()
        .size([width, height])
        .nodes(nodes)
        .links(links)
        .on("tick", tick)
        .gravity(0.5)
        .charge(-5000)
        .linkDistance(200)

      //Add links to SVG
      canvas.append("defs").append("marker")
        .attr("id", "arrow")
        .attr("viewBox", "0 -5 10 10")
        .attr('refX', 8)
        .attr('refY', 0)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M0,-5L10,0L0,5");

      let edges = canvas.append('g').selectAll("path")
        .data(force.links())

      edges.exit().remove()

      let path = edges.enter().append("path")
        .attr("class", "link")
        .style("stroke", "#ccc")
        .attr('marker-end', (d) => "url(#arrow)")
        .style("stroke-width", 2)


      //Add nodes to SVG
      let node = canvas.append('g').selectAll("circle")
        .data(nodes)

      node.exit()
        .transition().duration(1000)
        .attr('r', 0).remove()

      node.enter().append("g")
        .attr("class", "node")
        .call(force.drag)

      //Add circles to each node
      node.append("circle")
        .attr("r", radiusFunc)
        .attr("fill", d => {
          if (d.type == "sentiment") return sentimentColor[d.name]
          else if (d.type == "author") return "orange"
          else if (d.type == "comment") {
            if (d.parent_id == d.article_id) {
              return "pink"
            }
            return "#5EDA9E"
          } else return "cyan"

        }).on('click', articleClick)

      node.append("title")
        .text(d => {
          if (d.type == "comment") return d.body
          else if (d.type == "article") return d.title
          else return d.name
        })
      node.append('text')
        .attr("text-anchor", "middle")
        .attr("pointer-events", "none")
        .text(d => getNodeText(d))

      //Start the force layout calculation
      force.start()

      function tick() {
        path.attr("d", linkArc)
        node
          .attr("cx", d => d.x)
          .attr("cy", d => d.y)
          .attr("transform", transform);
      }

      function transform(d) {
        return "translate(" + d.x + "," + d.y + ")";
      }
    }
  }

  addRadioListener()

  function addRadioListener() {
    d3.selectAll('.radio-button')
      .on('click', function () {
        loadMapperGraph(mapperEndpoint + '?prop=' + this.value)
      })
  }

  // function linkArc(d) {
  //   var dx = d.target.x - d.source.x,
  //       dy = d.target.y - d.source.y,
  //       dr = Math.sqrt(dx * dx + dy * dy);
  //   return "M" + d.source.x + "," + d.source.y + "A" + dr + "," + dr + " 0 0,1 " + d.target.x + "," + d.target.y;
  // }

  function linkArc(d) {
    // Total difference in x and y from source to target
    diffX = d.target.x - d.source.x;
    diffY = d.target.y - d.source.y;

    // Length of path from center of source node to center of target node
    pathLength = Math.sqrt((diffX * diffX) + (diffY * diffY));

    // x and y distances from center to outside edge of target node
    offsetX = (diffX * d.target.radius) / pathLength;
    offsetY = (diffY * d.target.radius) / pathLength;

    return "M" + d.source.x + "," + d.source.y + "L" + (d.target.x - offsetX) + "," + (d.target.y - offsetY)
  }
})