

mapper_module.load_main = function load_main() {
    $.ajax({
      url: 'api/nodes/article',
      type: 'GET',
      success: function (json) {
        if (!('links' in json))
          json['links'] = []

        const nodes = json.nodes,
          links = json.links
        console.log("Main")
        console.log(json)
        mapper_module.render(nodes, links, mapper_module.main_canvas)
      },
      error: function (xhr, errormsg, error) {          
        console.log(error)
      }
    });
  }

  mapper_module.load_mapper =  function load_mapper (url = mapperEndpoint) {
    $.ajax({
      url: url,
      type: 'GET',
      success: function (json) {
        if (!('links' in json))
          json['links'] = []

        const nodes = json.nodes,
          links = json.links
        console.log("Mapper")
        console.log(nodes)
        mapper_module.render(nodes, links, mapper_module.mapper_canvas)
      },
      error: function (xhr, errormsg, error) {
        console.log(error)
      }
    });

}