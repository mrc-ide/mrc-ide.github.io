$(document).ready(function () {

    let individualNetwork,
        odinNetwork,
        orderlyNetwork,
        naomiNetwork;

    function drawGraph(elementId, graph) {

        const edges = new vis.DataSet(graph.edges);
        const nodes = new vis.DataSet(graph.nodes);

        // create a network
        const container = document.getElementById(elementId);
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
        return new vis.Network(container, visData, options);
    }

    $.get("odin-graph.json", function (graph) {
        odinNetwork = drawGraph("odin-graph", graph)
    });
    $.get("orderly-graph.json", function (graph) {
        orderlyNetwork = drawGraph("orderly-graph", graph)
    });
    $.get("naomi-graph.json", function (graph) {
        naomiNetwork = drawGraph("naomi-graph", graph)
    });
    $.get("individual-graph.json", function (graph) {
        individualNetwork = drawGraph("individual-graph", graph)
    });

    $("#odin-tab").on('shown.bs.tab', function (event) {
        odinNetwork.fit();
    });
    $("#orderly-tab").on('shown.bs.tab', function (event) {
        orderlyNetwork.fit();
    });
    $("#naomi-tab").on('shown.bs.tab', function (event) {
        naomiNetwork.fit();
    });
    $("#individual-tab").on('shown.bs.tab', function (event) {
        individualNetwork.fit();
    });
});
