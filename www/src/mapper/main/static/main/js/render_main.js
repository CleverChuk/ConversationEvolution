var height = mapper_module.height
var width = mapper_module.width
var margin = mapper_module.margin

//Create an SVG element and append it to the DOM
let svg = d3.select(".graph")
  .select("svg")
  .attr("width", width)
  .attr("height", height)
  .classed("svg-content-responsive", true)
  .attr("preserveAspectRatio", "xMinYMin meet")
  .attr("viewBox", "0 0 " + (height + margin.top + margin.bottom) + " " + (width + margin.left + margin.right))



let main_canvas = svg.append('g')
  .attr('class', 'canvas')
svg
  .call(d3.zoom().on("zoom", zoomed))
// Zoom functions 
function zoomed() {
  main_canvas.attr("transform", d3.event.transform)
}

main_canvas.append('g')
  .attr('class', 'edge-layer')

main_canvas.append('g')
  .attr('class', 'node-layer')

main_canvas.append("defs").append("marker")
  .attr("id", "arrow")
  .attr("viewBox", "0 -5 10 10")
  .attr('refX', 8)
  .attr('refY', 0)
  .attr("markerWidth", 6)
  .attr("markerHeight", 6)
  .attr("orient", "auto")
  .append("path")
  .attr("d", "M0,-5L10,0L0,5");

mapper_module.main_canvas = main_canvas

mapper_module.render = function render(nodes, links, canvas) {
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
    return "translate(" + d.x + "," + d.y + ")";
  }
}
mapper_module.renderMainAsTree = function render(root, canvas) {
  console.log("Entering renderMainAsTree")
  let get_tree = function (data) {
    const root = d3.hierarchy(data)
      .sort((a, b) => (a.height - b.height) || a.data.type.localeCompare(b.data.type));
    root.dx = 10;
    root.dy = width / (root.height + 1);
    return d3.cluster().nodeSize([root.dx, root.dy])(root);
  }

  // Create hierarchy
  root = get_tree(root)
  console.log("Tree", root)

  // Calculate bounding box dimensions
  let x0 = Infinity;
  let x1 = -x0;

  root.each(d => {
    if (d.x > x1) x1 = d.x;
    if (d.x < x0) x0 = d.x;
  });


  canvas.attr("viewBox", [0, 0, width, x1 - x0 + root.dx * 2]);
  canvas.attr("transform", `translate(${root.dy / 3},${root.dx - x0})`);

  // Bind data to the UI
  let nodeLayer = canvas.select(".node-layer")
  nodeLayer.selectAll(".node").remove()
  let node = nodeLayer.attr("stroke-linejoin", "round")
    .attr("stroke-width", 3)
    .selectAll("g")
    .data(root.descendants().reverse())
    .join("g")
    .attr("transform", d => `translate(${d.y},${d.x})`);

  let colors = {
    "positive": "green",
    "negative": "red",
    "neutral": "blue"
  }

  node.append("circle")
    .attr("fill", d => {
      if (d.data.type == "sentiment") {
        return sentiment_color[d.name]

      } else if (d.data.type == "author") {
        return $("#author_color").val()

      } else if (d.data.type == "comment") {

        return colors[d.data.sentiment]

      } else if (d.data.type == "subreddit") {
        return $("#subreddit_color").val()

      } else {
        return $("#article_color").val()
      }

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
  edgeLayer.selectAll('path').remove()
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