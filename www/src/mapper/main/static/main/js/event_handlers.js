mapper_module.add_radio_listener = function add_radio_listener() {
    d3.selectAll('.radio-button')
        .on('click', function () {
            mapper_module.load_mapper(mapper_module.mapperEndpoint + '?prop=' + this.value)
        })
}

mapper_module.article_click = function article_click (node) {
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
            },
            error: function (xhr, errormsg, error) {
                console.log(error)
            }
        });
    }
}