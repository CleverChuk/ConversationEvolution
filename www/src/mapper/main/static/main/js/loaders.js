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

mapper_module.load_mapper = function load_mapper(url = mapper_module.mapperEndpoint, filter) {
  $.ajax({
    url: url,
    type: 'GET',
    success: function (json) {
      if (!('links' in json))
        json['links'] = []

      const nodes = json.nodes,
        links = json.links
      mapper_module.render_mapper(nodes, links, mapper_module.mapper_canvas, filter)
      // mapper_module.render_mapper_as_scatter_plot(nodes, mapper_module.mapper_canvas, filter)
    },
    error: function (xhr, errormsg, error) {
      console.log(error)
    }
  });

}

mapper_module.load_tree_map = function load_tree_map(url = mapper_module.mapperEndpoint, filter) {

  // Make asynchornous query
  $.ajax({
    url: url,
    type: 'GET',
    success: function (json) {
      mapper_module.render_tree(json, mapper_module.mapper_canvas, filter)
    },
    error: function (xhr, errormsg, error) {
      console.log(error)
    }
  });

}