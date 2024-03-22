async function drawPrimary(lang) {

  const data = await d3.json("./static/primary.json");

  let primary_label = 'label_'+lang

  const curve = d3.line().curve(d3.curveBumpX);

  d3.select("#paper")
    .append("svg")
    .attr("id", "canvas")
    .attr("width", 600)
    .attr("height", 310)
    .style("background-color", "mediumaquamarine");
  
  let nodes = data['nodes']

  d3.select('#canvas')
    .selectAll('.entity_text')
    .data(nodes)
    .join('text')
    .attr("class", "entity_text")
    .attr("id", d => 'node_'+d.handle)
    .attr('x', d => d.x)
    .attr('y', d => d.y)
    .attr('font-family', 'Quicksand')
    .attr('font-family', 'Quicksand')
    .attr('font-size', '16px')
    .attr('text-anchor', 'middle')
    .attr('alignment-baseline', 'middle')
    .attr('stroke', 'black')
    .attr('fill', 'black')
    .text(d => d[primary_label])
  
  nodes.forEach((d) => d.box = d3.select("#node_"+d.handle).node().getBBox())
  
  let links = data['links']
  links.forEach((d) => d.x1 = nodes.filter((x) => x['handle'] == d['source'])[0]['x'])
  links.forEach((d) => d.y1 = nodes.filter((x) => x['handle'] == d['source'])[0]['y'])
  links.forEach((d) => d.x2 = nodes.filter((x) => x['handle'] == d['target'])[0]['x'])
  links.forEach((d) => d.y2 = nodes.filter((x) => x['handle'] == d['target'])[0]['y'])
  
  d3.select('#canvas')
    .selectAll('.links_yes')
    .data(links)
    .join('path')
    .attr("class", "links_yes")
    .attr('d', d => curve([[d.x1, d.y1], [d.x2, d.y2]]))
    .attr('stroke', 'black')
    .attr('fill', 'none');
  
  links.forEach((d) => d.x3 = (d.x1+d.x2)/2)
  links.forEach((d) => d.y3 = (d.y1+d.y2)/2)
  
  d3.select('#canvas')
    .selectAll('.entity_blocks')
    .data(nodes)
    .join('rect')
    .attr("class", "entity_blocks")
    .attr('width', d => d.box.width+10+10)
    .attr('height', d => d.box.height+10+10)
    .attr('x', d => d.box.x-10)
    .attr('y', d => d.box.y-10)
    .attr('stroke', 'black')
    .attr('stroke-width', '2px')
    .attr('fill', 'mediumaquamarine')
    .on("mouseover", function(k,d) {
      d3.select(this).attr('fill', 'black')
      d3.select('#'+d.handle+'box_text').attr('stroke', 'mediumaquamarine')
    })
    .on("mouseout", function() {
      d3.selectAll('.entity_blocks').attr('fill', 'mediumaquamarine')
      d3.selectAll('.entity_text2').attr('stroke', 'black')
    })
    .on("click", function(k, d) { window.open('https://ontology.fiafcore.org/'+d.url,"_self"); });
  
  d3.select('#canvas')
    .selectAll('.entity_text2')
    .data(nodes)
    .join('text')
    .attr("class", "entity_text2")
    .attr("id", d => d.handle+'box_text')
    .attr('x', d => d.x)
    .attr('y', d => d.y)
    .attr('font-family', 'Quicksand')
    .attr('font-size', '16px')
    .attr('font-weight', '100')
    .attr('text-anchor', 'middle')
    .attr('alignment-baseline', 'middle')
    .attr('stroke', 'black')
    .attr('fill', 'black')
    .text(d => d[primary_label])
    .style('pointer-events', 'none')
}

drawPrimary(lang);
