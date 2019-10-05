//This code uses version 3 of d3js
//Set margins and sizes
var margin = {
    top: 20,
    bottom: 50,
    right: 30,
    left: 50
}

var width = 960 - margin.left - margin.right
var height = 550 - margin.top - margin.bottom
var controls_width = 120
var data = null;

//Load Color Scale
var c10 = d3.scale.category10()

//Create an SVG element and append it to the DOM
var svg = d3.select(".graph")
    .append("svg")
    .classed("svg-content-responsive", true)
    .attr("preserveAspectRatio", "xMinYMin meet")
    .attr("viewBox", "0 0 " + (height + margin.top + margin.bottom) + " " + (width + margin.left + margin.right))
    .call(d3.behavior.zoom().on("zoom", function () {
        svg.attr("transform", "translate(" + d3.event.translate + ")" + " scale(" + d3.event.scale + ")")
    }))
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")")

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


//Load data
d3.json("mdata.json", graph => render(graph, mSvg))

//Load data
d3.json("data.json", graph => {
    addPropertyControl(graph.nodes)
    render(graph, svg)
})

// Functions
function render(graph, canvas) {
    data = graph
    radiusFunc = node => {
        return node.score / 5 > 10 ? node.score / 5 : 20
    }

    //Extract data from graph
    let nodes = graph.nodes,
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
    var link = canvas.selectAll(".link")
        .data(links)

    link.enter().append("line")
        .attr("stroke-width", "2")
        .attr("class", "link")
    link.exit().remove()

    //Add nodes to SVG
    var node = canvas.selectAll(".node")
        .data(nodes)
    node.enter().append("g")
        .attr("class", "node")
        .call(force.drag)

    //Add circles to each node
    node.append("circle")
        .attr("r", radiusFunc)
        .attr("fill", d => c10(d.type))

    node.append('title')
        .text(d => d.type)

    node.exit().remove()




    //This function will be executed once force layout is done with its calculations
    force.on("tick", function () {
        //Set X and Y of node
        node
            .attr("cx", d => d.x)
            .attr("cy", d => d.y)
            //Shift node a little
            .attr("transform", d => "translate(" + d.x + "," + d.y + ")")

        //Set X, Y of link
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y)

    })
    //Start the force layout calculation
    force.start()
}

function addPropertyControl(nodes) {
    let properties = null
    for (var i = 0; i < nodes.length; i++) {
        if (nodes[i].type == "comment") {
            properties = Object.getOwnPropertyNames(nodes[i])
            break;
        }
    }
    var row = document.createElement("div");
    row.className = "row";
    row.style.margin = "10px";

    var column = document.createElement("div");
    column.className = "col-12";
    column.style.display = "flex"
    column.style.display = "-webkit-flex"
    column.style.flexWrap = "wrap"

    row.appendChild(column);
    properties.forEach(prop => {
        var checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.className = "prop-control"

        var label = document.createElement("span");
        label.innerHTML = prop;
        label.style.marginLeft = "10px"
        label.style.marginRight = "10px"

        column.appendChild(checkbox);
        column.appendChild(label);
    })

    document.getElementsByClassName("container")[0].appendChild(row);
}

setUpControls()
function setUpControls() {
    d3.select('.ctrl1').on("click", () => {
        var nodes = data.nodes.filter(d => d.type == 'comment')
        var links = data.links.filter(d => {
            for (let i = 0; i < nodes.length; i++) {
                if (nodes[i].index == d.source.index || nodes[i].index == d.target.index)
                    return true
            }
            return false
        })
        var graph = {
            "nodes": nodes,
            "links": links
        }
        render(graph, svg)
    })

    d3.select('.ctrl2').on("click", () => {
        render(data, svg)
    })
}