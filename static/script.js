<script>
    var nodes = {{ nodes | safe }};
    var edges = {{ edges | safe }};
    console.log(edges);
    console.log(nodes);

    var svgContainer = d3.select("#svg-container");

    var width = svgContainer.node().getBoundingClientRect().width;
    var height = svgContainer.node().getBoundingClientRect().height;

    var svg = svgContainer.append("svg")
        .attr("width", width)
        .attr("height", height);
svg.append("defs")
  .append("marker")
  .attr("id", "arrowhead")
  .attr("viewBox", "0 -5 10 10") // Adjust the viewBox for arrowhead size
  .attr("refX", 10) // Adjust the refX to position the arrowhead at the end of the line
  .attr("refY", 0)
  .attr("markerWidth", 6) // Adjust the markerWidth for arrowhead size
  .attr("markerHeight", 6)
  .attr("orient", "auto") // Set the orientation of the arrowhead based on line direction
  .append("path")
  .attr("d", "M0,-5L10,0L0,5") // Path commands for the arrowhead shape
  .style("fill", "#999"); // Set the color of the arrowhead


    var simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(edges).id(d => d.id))
        .force("charge", d3.forceManyBody())
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("x", d3.forceX(width / 2).strength(0.001))
        .force("y", d3.forceY(height / 2).strength(0.001));

    var colorMap = {
      "Assignment statement": "red",
      "Location partially identifiable source": "orange",
      "Not a privacy-relevant method": "blue",
      "Nop statement": "green",
      "Identity statement": "purple",
      "Conditional statement": "yellow",
      "Processing method": "cyan",
      "Network identifiable source": "magenta",
      "Apache network method": "teal",
      "IO method": "brown",
      "Return statement": "pink"
    };
/*
    var link = svg.selectAll("line")
        .data(edges)
        .enter().append("line")
        .style("stroke", "#999");
*/
    var link = svg.selectAll("line")
  .data(edges)
  .enter().append("line")
  .style("stroke", "#999")
  .style("stroke-width", 2)
  .attr("marker-end", "url(#arrowhead)") // Add the arrowhead marker to the end of the line
  .attr("x1", d => d.source.x)
  .attr("y1", d => d.source.y)
  .attr("x2", d => d.target.x)
  .attr("y2", d => d.target.y);


    var node = svg.selectAll("circle")
        .data(nodes)
        .enter().append("circle")
        .attr("r", 5)
        .style("fill", d => colorMap[d.privacyRelevance] || "gray")
        .on("mouseover", handleMouseOver)
        .on("mouseout", handleMouseOut);

    var linkLabels = svg.selectAll(".link-label")
        .data(edges)
        .enter().append("text")
        .attr("class", "link-label")
        .attr("x", d => (d.source.x + d.target.x) / 2)
        .attr("y", d => (d.source.y + d.target.y) / 2)
        .text(d => d.edgeType);

    var nodeLabels = svg.selectAll(".node-label")
    .data(nodes)
    .enter().append("text")
    .attr("class", "node-label")
    .attr("x", d => d.x + 10)
    .attr("y", d => d.y - 10)
    .text(d => d.node);


    simulation.on("tick", () => {
      link
          .attr("x1", d => d.source.x)
          .attr("y1", d => d.source.y)
          .attr("x2", d => d.target.x)
          .attr("y2", d => d.target.y);

      node
          .attr("cx", d => d.x)
          .attr("cy", d => d.y);

      linkLabels
          .attr("x", d => (d.source.x + d.target.x) / 2)
          .attr("y", d => (d.source.y + d.target.y) / 2);

      nodeLabels
          .attr("x", d => d.x + 10)
          .attr("y", d => d.y - 10);
    });

    // Event handler for mouseover event
    function handleMouseOver(event, d) {
      d3.select(this).attr("r", 8); // Increase the circle size
      d3.select(this).attr("stroke", "black"); // Add a black stroke

      // Create a tooltip
      var tooltip = d3.select("body")
        .append("div")
        .attr("class", "tooltip")
        .style("position", "absolute")
        .style("background-color", "white")
        .style("border", "1px solid black")
        .style("padding", "5px")
        .style("left", event.pageX + "px")
        .style("top", event.pageY + "px");

      tooltip.append("div")
        .text("Privacy Relevance: " + d.privacyRelevance);

      tooltip.append("div")
        .text("Node: " + d.id);

      tooltip.append("div")
        .text("To Node: " + d.toNode);

      tooltip.append("div")
        .text("Additional Info: " + d.additionalInfo);

      tooltip.append("div")
        .text("Edge Type: " + d.edgeType);

    }

    // Event handler for mouseout event
    function handleMouseOut(event, d) {
      d3.select(this).attr("r", 5); // Restore the circle size
      d3.select(this).attr("stroke", "none"); // Remove the stroke

      // Remove the tooltip
      d3.select(".tooltip").remove();
    }
  </script>