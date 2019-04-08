var mapper_module = function () {}
// This code uses version 3 of d3js
// Set margins and sizes
mapper_module.mapperEndpoint = 'api/mapper';
mapper_module.margin = {
    top: 20,
    bottom: 50,
    right: 30,
    left: 50
}

mapper_module.width = 960 - mapper_module.margin.left - mapper_module.margin.right
mapper_module.height = 550 - mapper_module.margin.top - mapper_module.margin.bottom


//Load Color Scale
mapper_module.c10 = d3.scale.category10()
sentimentColor = {
    "positive": "#3AE71E",
    "negative": "red",
    "neutral": "blue"
}

mapper_module.render = function (nodes, links, canvas) {
    radiusFunc = node => {
        node.radius = 25
        return 25 //node.score / 5 > 10 ? node.score / 5 : 20
    }
    console.log("nodes")
    console.log(nodes)
    console.log("links")
    console.log(links)
    console.log("canvas")
    console.log(canvas)
    
    //Create Force Layout
    var force = d3.layout.force()
        .size([mapper_module.width, mapper_module.height])
        .nodes(nodes)
        .links(links)
        .on("tick", tick)
        .gravity(0.5)
        .charge(-5000)
        .linkDistance(200)

    var edges = canvas.append('g').selectAll("path")
        .data(force.links())

    edges.exit().remove()

    path = edges.enter().append("path")
        .attr("class", "link")
        .style("stroke", "#ccc")
        .attr('marker-end', (d) => "url(#arrow)")
        .style("stroke-width", 2)


    //Add nodes to SVG
    var node = canvas.append('g').selectAll("circle")
        .data(nodes)

    node.exit()
        .transition().duration(1000)
        .attr('r', 0).remove()

    node.enter().append("g")
        .attr("class", "node")
        .call(force.drag)

    //Add circles to each node
    node.append("circle")
        .attr("r", radiusFunc)
        .attr("fill", d => {
            if (d.type == "sentiment") {
                return sentimentColor[d.name]
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
        }).on('click', mapper_module.articleClick)

    node.append("title")
        .text(d => {
            if (d.type == "comment") return d.body
            else if (d.type == "article") return d.title
            else return d.name
        })
    node.append('text')
        .attr("text-anchor", "middle")
        .attr("pointer-events", "none")
        .text(d => mapper_module.getNodeText(d))

    //Start the force layout calculation
    force.start()
    var tick = function () {
        path.attr("d", linkArc);
        node.attr("transform", transform);
    }
    
    var transform = function (d) {
        return "translate(" + d.x + "," + d.y + ")";
    }
   var linkArc = function (d) {
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
}



mapper_module.addPropertyControl = function (nodes) {
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

 mapper_module.getNodeText = function (node) {
    if (node.type == "author") return node["name"]
    else if (node.type == "sentiment") return node["name"]
    else return node.type
  }