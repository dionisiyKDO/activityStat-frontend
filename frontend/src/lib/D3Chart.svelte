<script>
    import { onMount } from "svelte";
    import * as d3 from "d3";
  
    export let data = [];
  
    onMount(() => {
      const width = 800;
      const height = 400;
      const margin = { top: 20, right: 30, bottom: 40, left: 40 };
  
      const svg = d3
        .select("#chart")
        .attr("width", width)
        .attr("height", height);
  
      const x = d3
        .scaleBand()
        .domain(data.map((d) => d.app))
        .range([margin.left, width - margin.right])
        .padding(0.1);
  
      const y = d3
        .scaleLinear()
        .domain([0, d3.max(data, (d) => d.duration)])
        .nice()
        .range([height - margin.bottom, margin.top]);
  
      const tooltip = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("position", "absolute")
        .style("visibility", "hidden")
        .style("background-color", "white")
        .style("border", "solid 1px #000")
        .style("padding", "5px")
        .style("border-radius", "5px");
  
      svg
        .append("g")
        .selectAll("rect")
        .data(data)
        .join("rect")
        .attr("x", (d) => x(d.app))
        .attr("y", y(0))
        .attr("height", 0)
        .attr("width", x.bandwidth())
        .attr("fill", "steelblue")
        .on("mouseover", function(event, d) {
          tooltip
            .html(`App: ${d.app}<br>Duration: ${d.duration}`)
            .style("visibility", "visible");
          d3.select(this).attr("fill", "orange");
        })
        .on("mousemove", function(event) {
          tooltip
            .style("top", `${event.pageY - 10}px`)
            .style("left", `${event.pageX + 10}px`);
        })
        .on("mouseout", function() {
          tooltip.style("visibility", "hidden");
          d3.select(this).attr("fill", "steelblue");
        })
        .transition()
        .duration(750)
        .attr("y", (d) => y(d.duration))
        .attr("height", (d) => y(0) - y(d.duration));
  
      svg
        .append("g")
        .call(d3.axisLeft(y))
        .attr("transform", `translate(${margin.left},0)`);
  
      svg
        .append("g")
        .call(d3.axisBottom(x))
        .attr("transform", `translate(0,${height - margin.bottom})`);
    });
  </script>
  
  <svg id="chart"></svg>
  
  <style>
    svg {
      font: 10px sans-serif;
    }
    
    .axis path,
    .axis line {
      fill: none;
      shape-rendering: crispEdges;
    }
    .tooltip {
      position: absolute;
      text-align: center;
      width: auto;
      height: auto;
      padding: 5px;
      font: 12px sans-serif;
      background: lightsteelblue;
      border: 0px;
      border-radius: 8px;
      pointer-events: none;
    }
  </style>
  