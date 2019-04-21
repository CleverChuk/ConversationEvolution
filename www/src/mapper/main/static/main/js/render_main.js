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