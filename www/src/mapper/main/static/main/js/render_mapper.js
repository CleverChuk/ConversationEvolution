var height = mapper_module.height
var width = mapper_module.width
var margin = mapper_module.margin


var canvas = d3.select(".mgraph").append("svg")
.classed("svg-content-responsive", true)
.attr("preserveAspectRatio", "xMinYMin meet")
.attr("viewBox", "0 0 " + (height + margin.top + margin.bottom) + " " + (width + margin.left + margin.right))

canvas.call(d3.behavior.zoom().on("zoom", function () {
  canvas.attr("transform", "translate(" + d3.event.translate + ")" + " scale(" + d3.event.scale + ")")
}))
.append("g")
.attr("transform", "translate(" + margin.left + "," + margin.top + ")")

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

mapper_module.mCanvas = canvas