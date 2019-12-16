var params = null
var nodeId = null
mapper_module.article_click = function (node) {
    if (node.type == 'article') {
        d3.select('.legend')
            .text(node.title)

        nodeId = node.id
        let render = function () {
            var checked = $("#treemap").is(':checked');
            if (checked) {                
                $.each($(".filter").filter(":checked"), function () {
                    params = '?prop=' + this.value + "&epsilon=" + $("#epsilon-range").val() +
                        "&interval=" + $("#interval-count").val()
                    mapper_module.load_tree_map(`api/tree/${node.id}${params}`, this.value)
                    
                    console.log(`Sending request to endpoint: api/tree/${node.id}${params}`)
                })
            } else {
                // render article mapper graph as well based on the selected filter
                $.each($(".filter").filter(":checked"), function () {
                    params = '?prop=' + this.value + "&epsilon=" + $("#epsilon-range").val() +
                        "&interval=" + $("#interval-count").val()
                    mapper_module.load_mapper(mapper_module.mapperEndpoint + params, this.value)
                })
            }
        }

        $.ajax({
            url: `api/nodes/article/${node.id}`,
            type: 'GET',
            success: function (json) {
                const nodes = json.nodes,
                    links = json.links
                // Render main graph
                // mapper_module.render(nodes, links, mapper_module.main_canvas)
                console.log("Raw Data",json)
                mapper_module.renderMainAsTree(json, mapper_module.main_canvas)
                // Render mapper graph
                render()
            },
            error: function (xhr, errormsg, error) {
                console.log(error)
            }
        });
    }
}

mapper_module.add_slider_listeners = function () {
    var interval = document.getElementById("interval-count"),
        epsilon = document.getElementById("epsilon-range")

    interval.oninput = function () {
        $("#interval-value").text($("#interval-count").val())
//        graph()
    }

    epsilon.oninput = function () {
        $("#epsilon-value").text($("#epsilon-range").val())
//        graph()
    }

}

mapper_module.add_button_listener = function () {
    $("#graph-btn").on("click", graph)
}

function graph() {
    // read the state of the epsilon slider and interval slider and build API endpoint params
    params = `?interval= ${$("#interval-count").val()}`
        var checked = $("#treemap").is(':checked');
        if (checked) {                
                mapper_module.load_tree_map(`api/tree/${nodeId}${params}`)                
                console.log(`Sending request to endpoint: api/tree/${nodeId}${params}`)
        } 
    // read the selected filter
    $.each($(".filter").filter(":checked"), function () {
        let filter = this.value
        // Add filter param to endpoint
        params += '&prop=' + filter

        // // read the method of aggregation
        // $.each($(".a-method").filter(":checked"), function () {
        //     // Add the method of aggregation to endpoint
        //     params += '&mode=' + this.value

        //     //params API endpoint for data
        //     mapper_module.load_mapper(mapper_module.mapperEndpoint + params, filter)
        // })
    })
}