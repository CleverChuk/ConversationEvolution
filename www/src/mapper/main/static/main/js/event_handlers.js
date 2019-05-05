var query = null
mapper_module.article_click = function (node) {
    if (node.type == 'article') {
        d3.select('.legend')
            .text(node.title)

        $.ajax({
            url: 'api/nodes/article/' + node.id,
            type: 'GET',
            success: function (json) {
                mapper_module.add_property_control(json.nodes)

                const nodes = json.nodes,
                    links = json.links
                mapper_module.render(nodes, links, mapper_module.main_canvas)
                // render article mapper graph as well based on the selected filter
                $.each($(".filter").filter(":checked"), function () {
                    query = '?prop=' + this.value + "&epsilon=" + $("#epsilon-range").val() +
                        "&interval=" + $("#interval-count").val()
                    mapper_module.load_mapper(mapper_module.mapperEndpoint + query, this.value)
                })
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
    }

    epsilon.oninput = function () {
        $("#epsilon-value").text($("#epsilon-range").val())
    }

}

mapper_module.add_button_listener = function () {
    $("#graph-btn").on("click", function () {
        query = "?epsilon=" + $("#epsilon-range").val() +
            "&interval=" + $("#interval-count").val()

        $.each($(".filter").filter(":checked"), function () {
            query += '&prop=' + this.value

            $.each($(".a-method").filter(":checked"), function () {
                query += '&mode=' + this.value
                mapper_module.load_mapper(mapper_module.mapperEndpoint + query, this.value)
            })
        })
    })
}