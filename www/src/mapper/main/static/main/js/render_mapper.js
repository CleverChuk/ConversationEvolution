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
  .call(d3.behavior.zoom().on("zoom", function () {
    mapper_canvas.attr("transform", "translate(" + d3.event.translate + ")" + " scale(" + d3.event.scale + ")")
  }))

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

// V4
// mapper_module.zoom_handler(svg)
mapper_module.mapper_canvas = mapper_canvas