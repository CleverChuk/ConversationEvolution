mapper_module.addRadioListener = function () {
    d3.selectAll('.radio-button')
        .on('click', function () {
            mapper_module.mapper(mapperEndpoint + '?prop=' + this.value)
        })
}

mapper_module.articleClick = function (node) {
    if (node.type == 'article') {
        d3.select('.legend')
            .text(node.title)

        $.ajax({
            url: 'api/nodes/article/' + node.id,
            type: 'GET',
            success: function (json) {
                mapper_module.addPropertyControl(json.nodes)

                const nodes = json.nodes,
                    links = json.links
                mapper_module.render(nodes, links, mapper_module.mCanvas)
            },
            error: function (xhr, errormsg, error) {
                console.log(error)
            }
        });
    }
}