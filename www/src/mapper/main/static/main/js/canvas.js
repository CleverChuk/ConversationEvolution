export class Canvas {
    constructor() {
        if (this.instance) {
            return this.instance
        } else {
            var margin = {
                top: 20,
                bottom: 50,
                right: 30,
                left: 50
            }

            var width = 960 - margin.left - margin.right
            var height = 550 - margin.top - margin.bottom

            this.instance = new Canvas()
            this.blank_canvas = d3.select(".graph")
                .append("svg")
                .attr("width", width)
                .attr("height", height)
                .classed("svg-content-responsive", true)
                .attr("preserveAspectRatio", "xMinYMin meet")
                .attr("viewBox", "0 0 " + (height + margin.top + margin.bottom) + " " + (width + margin.left + margin.right))

            canvas = canvas
                .call(d3.behavior.zoom().on("zoom", function () {
                    canvas.attr("transform", "translate(" + d3.event.translate + ")" + " scale(" + d3.event.scale + ")")
                }))

                .append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

            return this.instance
        }
    }

    canvas() {
        return blank_canvas
    }
}