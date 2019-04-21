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
mapper_module.x_filter = null
mapper_module.y_filter = null

mapper_module.width = 960 - mapper_module.margin.left - mapper_module.margin.right
mapper_module.height = 550 - mapper_module.margin.top - mapper_module.margin.bottom


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

mapper_module.update_edges = function update_edges(canvas, links) {
    let layer = canvas.select('.edge-layer')
    let edges = layer.selectAll(".link").data(links)

    // Exit
    edges.exit().transition()
        .attr('duration', 1000)
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
    edges = edges.enter().append("path")
        .attr("class", "link")
        .merge(edges)

    // Update
    edges
        .style("stroke", "#ccc")
        .attr('marker-end', d => "url(#arrow)")
        .style("stroke-width", 2)

    return edges
}

mapper_module.update_nodes = function update_nodes(canvas, nodes, simulation) {
    var sentiment_color = {
        "positive": "#3AE71E",
        "negative": "red",
        "neutral": "blue"
    }
    var radiusFunc = node => {
        node.radius = 25
        return 25 //node.score / 5 > 10 ? node.score / 5 : 20
    }
    //Drag functions 
    var drag = simulation => {

        function dragstarted(d) {
            if (!d3.event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragged(d) {
            d.fx = d3.event.x;
            d.fy = d3.event.y;
        }

        function dragended(d) {
            if (!d3.event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }

        return d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended);
    }


    //Add circles to each node
    let layer = canvas.select('.node-layer')
    // Add a class and a unique id for proper update
    let circles = layer.selectAll('.node').data(nodes, d => d.id)

    // Exit
    circles.exit()
        .transition()
        .attr('duration', 1000)
        .attr('r', 20)
        .transition()
        .attr('duration', 1500)
        .attr('r', 10)
        .transition()
        .attr('duration', 1500)
        .attr('r', 0)
        .remove()
    // Enter
    circles = circles.enter().append('g')
        .attr('class', 'node')
        .merge(circles)
        .call(drag(simulation))


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

            } else if (d.type == "subreddit") {
                return "violet"

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