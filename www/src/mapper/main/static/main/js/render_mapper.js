var height = mapper_module.height
var width = mapper_module.width
var margin = mapper_module.margin


let msvg = d3.select(".mgraph")
  .select("svg")
  .attr("width", width)
  .attr("height", height)
  .classed("svg-content-responsive", true)
  .attr("preserveAspectRatio", "xMinYMin meet")
  .attr("viewBox", "0 0 " + (height + margin.top + margin.bottom) + " " + (width + margin.left + margin.right))


let mapper_canvas = msvg.append('g')
  .attr('class', 'canvas')
msvg
  .call(d3.zoom().on("zoom", zoomed))

// Zoom functions 
function zoomed() {
  mapper_canvas.attr("transform", d3.event.transform)
}

mapper_canvas.append('g')
  .attr('class', 'edge-layer')

mapper_canvas.append('g')
  .attr('class', 'node-layer')

mapper_canvas.append("defs").append("marker")
  .attr("id", "arrow")
  .attr("viewBox", "0 -5 10 10")
  .attr('refX', 8)
  .attr('refY', 0)
  .attr("markerWidth", 6)
  .attr("markerHeight", 6)
  .attr("orient", "auto")
  .append("path")
  .attr("d", "M0,-5L10,0L0,5");

mapper_module.mapper_canvas = mapper_canvas


mapper_module.render_mapper = function render(nodes, links, canvas, filter) {
  canvas.select('.y-axis').remove()
  canvas.select('.x-axis').remove()
  console.log(filter)
  // find maximum property value
  let max = d3.max(nodes.filter(d=> d.type == "comment"), n => {
    return +n[filter]
  })
  // find minimum property value
  let min = d3.min(nodes.filter(d=> d.type == "comment"), n => {
    return +n[filter]
  })

  // Create a color scale with minimum and maximum values
  let color_scale = d3.scaleLinear()
    .range([0, 1])
    .domain([min, max])
  // Create X scale
  let xscale = d3.scaleLinear()
    .domain([min, max])
    .range([0, mapper_module.width]);

  if ($('#x').is(":checked")) {

    // Add scales to axis
    var x_axis = d3.axisBottom()
      .scale(xscale);

    //Append group and insert axis
    canvas.append("g")
      .attr('class', 'x-axis')
      .attr('transform', 'translate(0,' + mapper_module.height + ')')
      .call(x_axis);
  }


  // Create X scale
  var yscale = d3.scaleLinear()
    .domain([d3.min(nodes, node => node[filter]), d3.max(nodes, node => node[filter])])
    .range([1000, 0]);

  if ($('#y').is(":checked")) {
    // Add scales to axis
    var y_axis = d3.axisLeft()
      .scale(yscale);

    //Append group and insert axis
    canvas.append("g")
      .attr('class', 'y-axis')
      .call(y_axis);
  }

  //set up the simulation and add forces  
  const body_force = d3.forceManyBody()
    .strength(-500)

  const link_force = d3.forceLink(links);
  link_force.distance(250)

  const simulation = d3.forceSimulation(nodes)
    .force("link", link_force)
    .force("charge", body_force)
    .force("center", d3.forceCenter(mapper_module.width / 2, mapper_module.height / 2));
  //add tick instructions: 
  simulation.on("tick", tick);

  //render edges
  links = mapper_module.update_edges(canvas, links)

  // render nodes
  nodes = mapper_module.update_nodes(canvas, nodes, simulation)

  nodes.selectAll("circle")
    .attr("fill", d => {
      if (d.type == "comment") {
        let t = color_scale(d[filter])
        return d3.interpolateBlues(t)
      }else{
        return $("#author_color").val()
      }
    })

  function tick() {
    links.attr("d", linkArc);
    nodes.attr("transform", transform);
  }

  function linkArc(d) {
    // Total difference in x and y from source to target
    if (d.source.type == 'comment' && d.target.type == 'comment') {
      if ($('#x').is(":checked")) {
        var diffX = xscale(d.target[filter]) - xscale(d.source[filter]);
        var diffY = d.target.y - d.source.y;

        // Length of path from center of source node to center of target node
        var pathLength = Math.sqrt((diffX * diffX) + (diffY * diffY));

        // x and y distances from center to outside edge of target node
        var offsetX = (diffX * d.target.radius) / pathLength;
        var offsetY = (diffY * d.target.radius) / pathLength;

        return "M" + xscale(d.source[filter]) + "," + d.source.y + "L" + (xscale(d.target[filter]) - offsetX) + "," + (d.target.y - offsetY)

      }

      if ($('#y').is(":checked")) {
        var diffX = d.target.x - d.source.x;
        var diffY = yscale(d.target[filter]) - yscale(d.source[filter]);

        // Length of path from center of source node to center of target node
        var pathLength = Math.sqrt((diffX * diffX) + (diffY * diffY));

        // x and y distances from center to outside edge of target node
        var offsetX = (diffX * d.target.radius) / pathLength;
        var offsetY = (diffY * d.target.radius) / pathLength;

        return "M" + d.source.x + "," + yscale(d.source[filter]) + "L" + (d.target.x - offsetX) + "," + (yscale(d.target[filter]) - offsetY)

      }
    }

    if (d.target.type == 'comment') {
      if ($('#x').is(":checked")) {
        var diffX = xscale(d.target[filter]) - d.source.x;
        var diffY = d.target.y - d.source.y;

        // Length of path from center of source node to center of target node
        var pathLength = Math.sqrt((diffX * diffX) + (diffY * diffY));

        // x and y distances from center to outside edge of target node
        var offsetX = (diffX * d.target.radius) / pathLength;
        var offsetY = (diffY * d.target.radius) / pathLength;

        return "M" + d.source.x + "," + d.source.y + "L" + (xscale(d.target[filter]) - offsetX) + "," + (d.target.y - offsetY)

      }

      if ($('#y').is(":checked")) {
        var diffX = d.target.x - d.source.x;
        var diffY = yscale(d.target[filter]) - d.source.y

        // Length of path from center of source node to center of target node
        var pathLength = Math.sqrt((diffX * diffX) + (diffY * diffY));

        // x and y distances from center to outside edge of target node
        var offsetX = (diffX * d.target.radius) / pathLength;
        var offsetY = (diffY * d.target.radius) / pathLength;

        return "M" + d.source.x + "," + d.source.y + "L" + (d.target.x - offsetX) + "," + (yscale(d.target[filter]) - offsetY)

      }
    }
    if (d.source.type == 'comment') {
      if ($('#x').is(":checked")) {
        var diffX = d.target.x - xscale(d.source[filter]);
        var diffY = d.target.y - d.source.y;

        // Length of path from center of source node to center of target node
        var pathLength = Math.sqrt((diffX * diffX) + (diffY * diffY));

        // x and y distances from center to outside edge of target node
        var offsetX = (diffX * d.target.radius) / pathLength;
        var offsetY = (diffY * d.target.radius) / pathLength;

        return "M" + xscale(d.source[filter]) + "," + d.source.y + "L" + (d.target.x - offsetX) + "," + (d.target.y - offsetY)

      }

      if ($('#y').is(":checked")) {
        var diffX = d.target.x - d.source.x;
        var diffY = d.target.y - yscale(d.source[filter]);

        // Length of path from center of source node to center of target node
        var pathLength = Math.sqrt((diffX * diffX) + (diffY * diffY));

        // x and y distances from center to outside edge of target node
        var offsetX = (diffX * d.target.radius) / pathLength;
        var offsetY = (diffY * d.target.radius) / pathLength;

        return "M" + d.source.x + "," + yscale(d.source[filter]) + "L" + (d.target.x - offsetX) + "," + (d.target.y - offsetY)

      }
    }

    var diffX = d.target.x - d.source.x;
    var diffY = d.target.y - d.source.y;

    // Length of path from center of source node to center of target node
    var pathLength = Math.sqrt((diffX * diffX) + (diffY * diffY));

    // x and y distances from center to outside edge of target node
    var offsetX = (diffX * d.target.radius) / pathLength;
    var offsetY = (diffY * d.target.radius) / pathLength;

    return "M" + d.source.x + "," + d.source.y + "L" + (d.target.x - offsetX) + "," + (d.target.y - offsetY)

  }

  function transform(d) {
    if (d.type == 'comment') {
      if ($('#x').is(":checked"))
        return "translate(" + xscale(d[filter]) + "," + d.y + ")";

      if ($('#y').is(":checked"))
        return "translate(" + d.x + "," + yscale(d[filter]) + ")";

    }

    return "translate(" + d.x + "," + d.y + ")";
  }
}