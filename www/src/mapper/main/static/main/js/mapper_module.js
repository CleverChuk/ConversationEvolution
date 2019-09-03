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




mapper_module.update_edges = function update_edges(canvas, links) {
    let layer = canvas.select('.edge-layer')
    let edges = layer.selectAll(".link").data(links)

    // Exit
    edges.exit().transition().duration(1000)
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
    nodes.forEach(n => {
        n.radius = +n.radius
    });

    function radiusFunc(node) {
        return Math.PI * Math.pow(node.radius, 2)
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
        .transition().duration(1000)
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
        .attr("id", d => d.id)
        .attr("fill", d => {
            if (d.type == "sentiment") {
                return sentiment_color[d.name]

            } else if (d.type == "author") {
                return $("#author_color").val()

            } else if (d.type == "comment") {
                if (d.parent_id == d.article_id) {
                    return $("#root_comment_color").val()
                }
                return $("#comment_color").val()

            } else if (d.type == "subreddit") {
                return $("#subreddit_color").val()

            } else {
                return $("#article_color").val()
            }

        }).on('click', mapper_module.article_click)

    // Set the title attribute
    circles
        .append("title")
        .text(d => {
            if (d.type == "comment") return d.body
            else if (d.type == "article") return d.title
            else return d.name
        })
    // Set the text attribute
    circles
        .append('text')
        .attr("text-anchor", "middle")
        .attr("pointer-events", "none")
        .text(d => mapper_module.get_node_text(d))
    return circles
}

mapper_module.get_node_text = function get_node_text(node) {
    if (node.type == "author") return node["name"]
    else if (node.type == "sentiment") return node["name"]
    else return node.type
}