mapper_module.load_main = function load_main() {
  $.ajax({
    url: 'api/subreddit',
    type: 'GET',
    success: function (json) {
      if (!('links' in json))
        json['links'] = []

      const nodes = json.nodes,
        links = json.links
      mapper_module.render(nodes, links, mapper_module.main_canvas)
    },
    error: function (xhr, errormsg, error) {
      console.log(error)
    }
  });
}

mapper_module.load_mapper = function load_mapper(url = mapperEndpoint) {
  $.ajax({
    url: url,
    type: 'GET',
    success: function (json) {
      if (!('links' in json))
        json['links'] = []

      const nodes = json.nodes,
        links = json.links
      mapper_module.render_mapper(nodes, links, mapper_module.mapper_canvas,
         mapper_module.x_filter, mapper_module.y_filter)
    },
    error: function (xhr, errormsg, error) {
      console.log(error)
    }
  });

}