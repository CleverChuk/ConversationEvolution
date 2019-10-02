//This code uses version 3 of d3js
//Set margins and sizes
var margin = {
    top: 20,
    bottom: 50,
    right: 30,
    left: 50
}

var width = 1080 - margin.left - margin.right
var height = 500 - margin.top - margin.bottom

//Load Color Scale
var c10 = d3.scale.category10()


//Create an SVG element and append it to the DOM
var svg = d3.select("body")
    .append("svg")
    .attr({
        "width": width + margin.left + margin.right,
        "height": height + margin.top + margin.bottom
    })
    .call(d3.behavior.zoom().on("zoom", function () {
        main_graph.attr("transform", "translate(" + d3.event.translate + ")" + " scale(" + d3.event.scale + ")")
    }))
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")")

//Load data for main graph
d3.json("data.json", function (graph) {
    //Extract data from graph
    var nodes = graph.nodes,
        links = graph.links
    //Create Force Layout
    var force = d3.layout.force()
        .size([width, height])
        .nodes(nodes)
        .links(links)
        .gravity(0.05)
        .charge(-200)
        .linkDistance(200)

    //Add links to SVG
    var link = main_graph.selectAll(".link")
        .data(links)
        .enter()
        .append("line")
        .attr("stroke-width", function (d) {
            return 2
        })
        .attr("class", "link")

    //Add nodes to SVG
    var node = main_graph.selectAll(".node")
        .data(nodes)
        .enter()
        .append("g")
        .attr("class", "node")
        .call(force.drag)

    //Add labels to each node
    var label = node.append("text")
        .attr("dx", 12)
        .attr("dy", "0.35em")
        .attr("font-size", "12")
        .text(function (d) {
            return d.type
        })

    //Add circles to each node
    var circle = node.append("circle")
        .attr("r", function (d) {
            return d.score / 5 > 10 ? d.score / 5 : 10
        })
        .attr("fill", function (d) {
            return c10(d.type)
        })

    //This function will be executed once force layout is done with its calculations
    force.on("tick", function () {
        //Set X and Y of node
        node.attr("r", function (d) {
                return 5
            })
            .attr("cx", function (d) {
                return d.x
            })
            .attr("cy", function (d) {
                return d.y
            })
        //Set X, Y of link
        link.attr("x1", function (d) {
            return d.source.x
        })
        link.attr("y1", function (d) {
            return d.source.y
        })
        link.attr("x2", function (d) {
            return d.target.x
        })
        link.attr("y2", function (d) {
            return d.target.y
        })
        //Shift node a little
        node.attr("transform", function (d) {
            return "translate(" + d.x + "," + d.y + ")"
        })
    })

    //Start the force layout calculation
    force.start()
})