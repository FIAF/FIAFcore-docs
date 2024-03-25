
// order columns for dendo chart.

subject_node = [{'uri':'', 'label':''}]
console.log(blab)
parent_node = blab['parents']
child_node = blab['children']

// useful function

function customFunction(m, n, p) {
    let startValue = (m*50/2) - (n - 1) * 25;
    const increment = 50;
    const result = Array.from({ length: n }, (_, index) => startValue + index * increment);
    return result[p];
}

// required processing

const curve = d3.line().curve(d3.curveBumpX);
max = Math.max(subject_node.length, parent_node.length, child_node.length)

// svg

d3.select("#paper")
    .append("svg")
    .attr("id", "canvas")
    .attr("width", 800)
    .attr("height", max*50)
    // .attr("overflow", 'visible')
    // .style("background-color", "#fafafa");
    // .style("background-color", "lime");

// node location processing.

parent_node.forEach((d, i) => d["y"] = customFunction(max, parent_node.length, i))
parent_node.forEach((d, i) => d["x"] = 100) 

subject_node.forEach((d, i) => d["y"] = customFunction(max, subject_node.length, i)) 
subject_node.forEach((d, i) => d["x"] = 350) 

child_node.forEach((d, i) => d["y"] = customFunction(max, child_node.length, i)) 
child_node.forEach((d, i) => d["x"] = 600) 
 
// mandatory extract of processed data.

const subject_x = subject_node[0]['x']
const subject_y = subject_node[0]['y']

// line graphing.

function line_elements(data){
    d3.select('#canvas')
    .selectAll('g')
    .data(data)
    .join('path')
    .attr('d', d => curve([[d['x'], d['y']], [subject_x, subject_y]]))
    .style('stroke', 'black')
    .style('fill', 'none')
}

Array(parent_node, subject_node, child_node).forEach(d =>  line_elements(d))

// third processing, nodes themselves 

function circle_elements(data, int){
    d3.select('#canvas')
    .selectAll('g')
    .data(data)
    .join('circle')
    .attr('cx', (d,i) => d['x'])
    .attr('cy', (d,i) => d['y'])
    .attr('r', 5)
    .attr('fill', d => { if (int==1) {return 'white'} else{ return '#006666'}})
    .attr('stroke', d => { if (int==1) {return 'black'} else{ return 'white'}})
    // .attr('stoke-width', '2px')
    // .on("mouseover", function(k,d) {
    //     d3.select(this).attr('fill', 'orange')
    // })
    // .on("mouseout", function(k,d) {
    //     console.log(d)
    //     d3.selectAll('circle').attr('fill', d => { if (int==1) {return 'white'} else{ return '#006666'}})
    // })
    .on("click", function(k, d) { 
        window.open(d.url,"_self"); 
    });
}

Array(parent_node, subject_node, child_node).forEach((d, i) =>  circle_elements(d, i))

// fourth processing, text elements

function text_elements(data, i){

    let align = ['end', 'middle', 'start']
    let placement = (i-1)*10

    d3.select('#canvas')
        .selectAll('g')
        .data(data)
        .join('text')
        .attr('font-family', "Quicksand")
        .attr('font-weight', '800')
        .attr('font-size', '16px')
        // .attr('color', '#006666')
        // .style('color', '#006666')
        // .attr('color', 'green')
        .style('fill', '#006666')        
        .style('opacity', '1')
        .attr('x', (d,i) => d['x']+placement)
        .attr('y', (d,i) => d['y'])
        .attr('alignment-baseline', 'middle')
        .attr('text-anchor', align[i])
        .text(d => d.value)
}

Array(parent_node, subject_node, child_node).forEach((d, i) =>  text_elements(d, i))