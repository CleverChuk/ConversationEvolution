height = mapper_module.height
width = mapper_module.width
margin = mapper_module.margin


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

// mapper_canvas.append("defs").append("marker")
//   .attr("id", "arrow")
//   .attr("viewBox", "0 -5 10 10")
//   .attr('refX', 8)
//   .attr('refY', 0)
//   .attr("markerWidth", 6)
//   .attr("markerHeight", 6)
//   .attr("orient", "auto")
//   .append("path")
//   .attr("d", "M0,-5L10,0L0,5");

mapper_module.mapper_canvas = mapper_canvas


mapper_module.render_mapper = function render(nodes, links, canvas, filter) {
  canvas.select('.y-axis').remove()
  canvas.select('.x-axis').remove()

  // find maximum property value
  let max = d3.max(nodes.filter(d => d.type == "comment"), n => {
    return +n[filter]
  })
  // find minimum property value
  let min = d3.min(nodes.filter(d => d.type == "comment"), n => {
    return +n[filter]
  })

  // Create a color scale with minimum and maximum values
  let color_scale = d3.scaleLinear()
    .range([0, 1])
    .domain([min, max])
  // Create X scale
  let xscale = d3.scaleLinear()
    .domain([min, max])
    .range([0, width]);

  if ($('#x').is(":checked")) {

    // Add scales to axis
    var x_axis = d3.axisBottom()
      .scale(xscale);

    //Append group and insert axis
    canvas.append("g")
      .attr('class', 'x-axis')
      .attr('transform', 'translate(0,' + height + ')')
      .call(x_axis);
  }


  // Create Y scale
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
    .force("center", d3.forceCenter(width / 2, height / 2));
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
      } else {
        return $("#author_color").val()
      }
    })
    .on("mouseover", handle_mouse_over)
    .on("mouseout", handle_mouse_out);

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

mapper_module.render_mapper_as_scatter_plot = function render(nodes, canvas, filter) {
  canvas.select('.y-axis').remove()
  canvas.select('.x-axis').remove()
  nodes = nodes.filter(n => n.type == "comment")
  // find maximum property value
  let max = d3.max(nodes.filter(d => d.type == "comment"), n => {
    return +n[filter]
  })
  // find minimum property value
  let min = d3.min(nodes.filter(d => d.type == "comment"), n => {
    return +n[filter]
  })

  // Convert timestamp to date objects
  nodes.forEach(element => {
    let d = new Date(1970, 0, 1)
    d.setSeconds(+element['timestamp'])
    element['timestamp'] = d
  });


  // Create a color scale with minimum and maximum values
  let color_scale = d3.scaleLinear()
    .range([0, 1])
    .domain([min, max])

  // Create X scale
  let xscale = d3.scaleTime()
    .domain(d3.extent(nodes, d => d.timestamp))
    .range([0, width]);

  // Add scales to x axis
  var x_axis = d3.axisBottom()
    .scale(xscale);

  //Append x axis
  canvas.append("g")
    .attr('class', 'x-axis')
    .attr('transform', 'translate(0,' + (height + 10) + ')')
    .call(x_axis)
  canvas
    .append("text")
    .attr("class", "label")
    .attr("x", width / 2)
    .attr("y", height)
    .attr("dy", "5em")
    .style("text-anchor", "end")
    .text("Time");

  // Create Y scale
  var yscale = d3.scaleLinear()
    .domain([min, max])
    .range([height, min * 0.5]);

  // Add scales to axis
  var y_axis = d3.axisLeft()
    .scale(yscale);

  //Append group and insert axis
  canvas.append("g")
    .attr('class', 'y-axis')
    .call(y_axis)
  canvas
    .append("text")
    .attr("class", "label")
    .attr("transform", "rotate(-90)")
    .attr("y", height / 2)
    .attr("dx", "-10em")
    .attr("dy", "-18em")
    .style("text-anchor", "end")
    .text(filter);

  // Update selection
  const update = canvas.selectAll("rect")
    .data(nodes)
  update
    .attr("x", d => xscale(+d.timestamp))
    .attr("y", d => yscale(+d[filter]))

  // Enter selection
  const enter = update.enter()
  enter.append("rect")
    .attr("x", d => xscale(+d.timestamp))
    .attr("y", d => yscale(+d[filter]))
    .attr("height", 20)
    .attr("width", d => d.radius)
    .attr("fill", d => {
      if (d.type == "comment") {
        let t = color_scale(d[filter])
        return d3.interpolateBlues(t)
      } else {
        return $("#author_color").val()
      }
    })
    .on("mouseover", handle_mouse_over)
    .on("mouseout", handle_mouse_out);

  // Exit selection
  update.exit()
    .remove()

}

mapper_module.render_tree = function render(root, canvas, filter) {
  let get_tree = function (data) {
    const root = d3.hierarchy(data)
      .sort((a, b) => (a.height - b.height) || a.data.type.localeCompare(b.data.type));
    root.dx = 10;
    root.dy = width / (root.height + 1);
    return d3.cluster().nodeSize([root.dx, root.dy])(root);
  }

  // Create hierarchy
    root = get_tree(root)
  // find maximum property value
  let maximum = -Infinity
  // find minimum property value
  let minimum = Infinity
  // Calculate bounding box dimensions
  let x0 = Infinity;
  let x1 = -x0;

  let colors = {
    "positive": "green",
    "negative": "red",
    "neutral": "blue"
  }

  root.each(d => {
    if (d.x > x1) x1 = d.x;
    if (d.x < x0) x0 = d.x;
    if (typeof (d.data.value) != "string") {
      if (maximum < d.data.value) maximum = d.data.value
      if (minimum > d.data.value) minimum = d.data.value
    } else {
      if (maximum < d.data[filter]) maximum = d.data[filter]
      if (minimum > d.data[filter]) minimum = d.data[filter]
    }
  });
  // Create a color scale with minimum and maximum values
  let color_scale = d3.scaleLinear()
    .range([0, 1])
    .domain([minimum, maximum])

  canvas.attr("viewBox", [0, 0, width, x1 - x0 + root.dx * 2]);
  canvas.attr("transform", `translate(${root.dy / 3},${root.dx - x0})`);

  // Bind data to the UI
  let nodeLayer = canvas.select(".node-layer")
  let node = nodeLayer.attr("stroke-linejoin", "round")
    .attr("stroke-width", 3)
    .selectAll("g")
    .data(root.descendants().reverse())
    .join("g")
    .attr("transform", d => `translate(${d.y},${d.x})`);

  node.append("circle")
    .attr("fill", d => {

      if (typeof (d.data.value) == "string")
        return colors[d.data.value]

      let t = color_scale(d.data[filter])
      // return d3.interpolateBlues(t)
      return colors[d.data.sentiment]
    })
    .attr("r", 5);

  node.append("title")
    .attr("dy", "0.31em")
    .attr("x", d => d.children ? -6 : 6)
    .text(d => {
      if (d.data.body) return d.data.body
      return d.data.type
    })
    .filter(d => d.children)
    .attr("text-anchor", "end")
    .clone(true).lower()
    .attr("stroke", "white");

  let edgeLayer = canvas.select(".edge-layer")
  edgeLayer.attr("fill", "none")
    .attr("stroke", "#555")
    .attr("stroke-opacity", 0.4)
    .attr("stroke-width", 1.5)
    .selectAll("path")
    .data(root.links())
    .join("path")
    .attr("d", d => `
      M${d.target.y},${d.target.x}
      C${d.source.y + root.dy / 2},${d.target.x}
       ${d.source.y + root.dy / 2},${d.source.x}
       ${d.source.y},${d.source.x}
    `);
}

function handle_mouse_over(d, i) {
  let composition = d.composition
  let nodes = d3.select(".graph")
    .select("svg")
    .select(".node-layer")
    .selectAll(".node")

  d3.select(".graph")
    .select("svg")
    .select(".edge-layer")
    .attr('opacity', 0)

  nodes.attr("opacity", function (data) {
    if (typeof (composition[data.id]) == "undefined")
      return 0
  })
}

function handle_mouse_out(d, i) {
  let composition = d.composition
  let nodes = d3.select(".graph")
    .select("svg")
    .select(".node-layer")
    .selectAll(".node")

  d3.select(".graph")
    .select("svg")
    .select(".edge-layer")
    .attr('opacity', 1)

  nodes.attr("opacity", function (data) {
    if (typeof (composition[data.id]) == "undefined")
      return 1
  })
}