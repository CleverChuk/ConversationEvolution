$(
    mapper_module.load_main(),

//    mapper_module.add_slider_listeners(),

    mapper_module.add_button_listener(),

    $("#show").on("click", function () {
        mapper_module.load_main()
    }),

    $("#epsilon-value").text($("#epsilon-range").val()),

    $("#interval-value").text($("#interval-count").val()),
)