function drawGraph(elementId, graph) {

    const edges = new vis.DataSet(graph.edges);
    const nodes = new vis.DataSet(graph.nodes);

    // create a network
    const container = document.getElementById(elementId);
    if (container) {
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
            }
        };
        return new vis.Network(container, visData, options);
    }
}
