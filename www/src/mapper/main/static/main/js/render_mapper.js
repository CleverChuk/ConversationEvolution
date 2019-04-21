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


mapper_module.render_mapper = function render(nodes, links, canvas, x_filter = null, y_filter = null) {

  if (x_filter != null) {
    // Create X scale
    var xscale = d3.scaleLinear()
      .domain([d3.min(nodes, node => node[x_filter]), d3.max(nodes, node => node[x_filter])])
      .range([0, mapper_module.width - 50]);

    // Add scales to axis
    var x_axis = d3.axisBottom()
      .scale(xscale);

    //Append group and insert axis
    canvas.select('.x-axis').remove()
    canvas.append("g")
      .attr('class', 'x-axis')
      .attr('transform', 'translate(0,' + (mapper_module.height - mapper_module.margin.bottom) + ')')
      .call(x_axis);
  }

  if (y_filter != null) {
    // Create X scale
    var yscale = d3.scaleLinear()
      .domain([d3.min(nodes, node => node[y_filter]), d3.max(nodes, node => node[y_filter])])
      .range([0, mapper_module.width - 50]);

    // Add scales to axis
    var y_axis = d3.axisLeft()
      .scale(yscale);

    //Append group and insert axis
    canvas.select('.y-axis').remove()
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

  function tick() {
    links.attr("d", linkArc);
    nodes.attr("transform", transform);
  }

  function linkArc(d) {
    // Total difference in x and y from source to target
    if (d.source.type == 'comment') {
      // if (x_filter != null && y_filter != null) {
      //   var diffX = d.target[x_filter] - d.source[x_filter];
      //   var diffY = d.target[y_filter] - d.source[y_filter];

      //   // Length of path from center of source node to center of target node
      //   var pathLength = Math.sqrt((diffX * diffX) + (diffY * diffY));

      //   // x and y distances from center to outside edge of target node
      //   var offsetX = (diffX * d.target.radius) / pathLength;
      //   var offsetY = (diffY * d.target.radius) / pathLength;

      //   return "M" + d.source[x_filter] + "," + d.source[y_filter] + "L" + (d.target[x_filter] - offsetX) + "," + (d.target[y_filter] - offsetY)

      // }
      if (x_filter != null && y_filter == null) {
        var diffX = d.target[x_filter] - d.source[x_filter];
        var diffY = d.target.y - d.source.y;

        // Length of path from center of source node to center of target node
        var pathLength = Math.sqrt((diffX * diffX) + (diffY * diffY));

        // x and y distances from center to outside edge of target node
        var offsetX = (diffX * d.target.radius) / pathLength;
        var offsetY = (diffY * d.target.radius) / pathLength;

        return "M" + d.source[x_filter] + "," + d.source.y + "L" + (d.target[x_filter] - offsetX) + "," + (d.target.y - offsetY)

      }
      if (x_filter == null && y_filter != null) {
        var diffX = d.target.x - d.source.x;
        var diffY = d.target[y_filter] - d.source[y_filter];

        // Length of path from center of source node to center of target node
        var pathLength = Math.sqrt((diffX * diffX) + (diffY * diffY));

        // x and y distances from center to outside edge of target node
        var offsetX = (diffX * d.target.radius) / pathLength;
        var offsetY = (diffY * d.target.radius) / pathLength;

        return "M" + d.source.x + "," + d.source[y_filter] + "L" + (d.target.x - offsetX) + "," + (d.target[y_filter] - offsetY)

      }
    } else {
      var diffX = d.target.x - d.source.x;
      var diffY = d.target.y - d.source.y;

      // Length of path from center of source node to center of target node
      var pathLength = Math.sqrt((diffX * diffX) + (diffY * diffY));

      // x and y distances from center to outside edge of target node
      var offsetX = (diffX * d.target.radius) / pathLength;
      var offsetY = (diffY * d.target.radius) / pathLength;

      return "M" + d.source.x + "," + d.source.y + "L" + (d.target.x - offsetX) + "," + (d.target.y - offsetY)
    }
  }

  function transform(d) {
    if (d.type == 'comment') {
      if (x_filter != null && y_filter == null)
        return "translate(" + d[x_filter] + "," + d.y + ")";

      if (y_filter != null && x_filter == null)
        return "translate(" + d.x + "," + d[y_filter] + ")";


      return "translate(" + d[x_filter] + "," + d[y_filter] + ")";

    } else
      return "translate(" + d.x + "," + d.y + ")";
  }
}