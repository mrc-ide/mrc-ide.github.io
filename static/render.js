$(document).ready(function () {

    $.get("graph.json", function (graph) {

        const edges = new vis.DataSet(graph.edges);
        const nodes = new vis.DataSet(graph.nodes);

        // create a network
        const container = document.getElementById("mynetwork");
        const visData = {
            nodes: nodes,
            edges: edges
        };
        const options = {
            edges: {
                arrows: 'from'
            },
            nodes: {
                shape: "dot"
            },
            interaction: {
                navigationButtons: true
            },
            physics: {
                enabled: false
            },
        };
        const network = new vis.Network(container, visData, options);
        network.moveTo({scale: 0.8});
    });
});
