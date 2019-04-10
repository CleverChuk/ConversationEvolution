function mapper_module() {
    // This code uses version 3 of d3js
    // Set margins and sizes
}

mapper_module.mapperEndpoint = 'api/mapper';
mapper_module.margin = {
    top: 20,
    bottom: 50,
    right: 30,
    left: 50
}

mapper_module.width = 960 - mapper_module.margin.left - mapper_module.margin.right
mapper_module.height = 550 - mapper_module.margin.top - mapper_module.margin.bottom


mapper_module.render = function render(nodes, links, canvas) {

    //Create Force Layout
    var force = d3.layout.force()
        .size([mapper_module.width, mapper_module.height])
        .nodes(nodes)
        .links(links)
        .on("tick", tick)
        .gravity(0.5)
        .charge(-2500)
        .linkDistance(200)


    // render edges
    links = mapper_module.update_edges(canvas, force.links())

    // render nodes
    nodes = mapper_module.update_node(canvas, force)

    //Start the force layout calculation
    force.start()

    // VERSION 4
    // render edges
    // links = mapper_module.update_edges(canvas, links)

    // // render nodes
    // nodes = mapper_module.update_node(canvas, nodes)
   
    // var simulation = d3.forceSimulation(nodes)
    //     .force("charge", d3.forceManyBody().strength(-1000))
    //     .force("link", d3.forceLink(links).distance(200))
    //     .force("x", d3.forceX())
    //     .force("y", d3.forceY())
    //     .alphaTarget(1)
    //     .on("tick", tick);

    // // Update and restart the simulation.
    // simulation.nodes(nodes);
    // simulation.force("link").links(links);
    // simulation.alpha(1).restart();


    function tick() {
        links.attr("d", mapper_module.linkArc);
        nodes.attr("transform", transform);
    }

    function transform(d) {
        return "translate(" + d.x + "," + d.y + ")";
    }
}
mapper_module.update_edges = function update_edges(canvas, links) {
    let layer = canvas.select('.edge-layer')
    let edges = layer.selectAll(".link").data(links)

    // Exit
    edges.exit().transition()
        .attr("stroke-opacity", 0)
        .attrTween("x1", function (d) {
            return function () {
                return d.source.x;
            };
        })
        .attrTween("x2", function (d) {
            return function () {
                return d.target.x;
            };
        })
        .attrTween("y1", function (d) {
            return function () {
                return d.source.y;
            };
        })
        .attrTween("y2", function (d) {
            return function () {
                return d.target.y;
            };
        })
        .remove();

    // Enter
    edges.enter().append("path")
        .attr("class", "link")

    // Update
    edges
        .style("stroke", "#ccc")
        .attr('marker-end', d => "url(#arrow)")
        .style("stroke-width", 2)

    return edges
}

mapper_module.update_node = function update_node(canvas, force) {
    var sentiment_color = {
        "positive": "#3AE71E",
        "negative": "red",
        "neutral": "blue"
    }
    var radiusFunc = node => {
        node.radius = 25
        return 25 //node.score / 5 > 10 ? node.score / 5 : 20
    }

    //Add circles to each node
    let layer = canvas.select('.node-layer')
    // Add a class and a unique id for proper update
    nodes = force.nodes()
    let circles = layer.selectAll('.node').data(nodes, d => d.id)

    // Exit
    circles.exit()
        .transition()
        .attr('duration', 10000)
        .attr('r', 0)
        .remove()
    // Enter
    circles.enter().append('g')
        .attr('class', 'node')
        .call(force.drag)

    // Update
    circles.append('circle')
        .attr("r", radiusFunc)
        .attr("fill", d => {
            if (d.type == "sentiment") {
                return sentiment_color[d.name]

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

        }).on('click', mapper_module.article_click)

    circles
        .append("title")
        .text(d => {
            if (d.type == "comment") return d.body
            else if (d.type == "article") return d.title
            else return d.name
        })
    circles
        .append('text')
        .attr("text-anchor", "middle")
        .attr("pointer-events", "none")
        .text(d => mapper_module.get_node_text(d))

    // Version 4
    // mapper_module.drag_handler(circles)
    return circles
}

mapper_module.add_property_control = function add_property_control(nodes) {
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

mapper_module.get_node_text = function get_node_text(node) {
    if (node.type == "author") return node["name"]
    else if (node.type == "sentiment") return node["name"]
    else return node.type
}

mapper_module.linkArc = function linkArc(d) {
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

// D3js V4
//Drag functions 
// d is the node 
// mapper_module.drag_start = function drag_start(d) {
//     if (!d3.event.active) simulation.alphaTarget(0.3).restart();
//     d.fx = d.x;
//     d.fy = d.y;
// }

// // make sure you can't drag the circle outside the box
// mapper_module.drag = function drag(d) {
//     d.fx = d3.event.x;
//     d.fy = d3.event.y;
// }

// mapper_module.drag_end = function drag_end(d) {
//     if (!d3.event.active) simulation.alphaTarget(0);
//     d.fx = null;
//     d.fy = null;
// }

// // Zoom functions 
// mapper_module.zoom = function zoom_actions(g) {
//     g.attr("transform", d3.event.transform)
// }

// // add drag capabilities  
// mapper_module.drag_handler = d3.drag()
//     .on("start", mapper_module.drag_start)
//     .on("drag", mapper_module.drag_drag)
//     .on("end", mapper_module.drag_end);

// // add zoom capabilities 
// mapper_module.zoom_handler = d3.zoom()
//     .on("zoom", mapper_module.zoom_actions);