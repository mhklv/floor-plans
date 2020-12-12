
var svg = d3.select("svg"),
        width = +svg.attr("width"),
        height = +svg.attr("height");

    var simulation = d3.forceSimulation()
        .force("link", d3.forceLink().id(function(d) { return d.id; }).distance(40))
        .force("x", d3.forceX(width / 2))
        .force("y", d3.forceY(height / 2))
        .on("tick", ticked);

    var link = svg.selectAll(".link"),
        node = svg.selectAll(".node");


    simulation.nodes(graph.nodes);
    simulation.force("link").links(graph.links);

    link = link     
        .data(graph.links)
        .enter().append("line")
        .attr("class", "link");

    count = 0;
    first = 0;
    second = 0;
    svg
    .on("click", function(d){
        let coords = d3.mouse(this);
        let click_id = coordinates(parseInt(coords[0]), parseInt(coords[1]));
        if(count === 0) {
            svg.select("#n_" + click_id)
                .transition(1000)
                .duration(1000)
                .style("opacity", "1")
            first = click_id;
            count++;
        } else if(count == 1) {
            if(first != d3.select("#n_" + click_id)) {
                second = click_id;
                svg.select("#n_" + click_id)
                    .transition(1000)
                    .duration(1000)
                    .style("opacity", "1");
                count++;
            }
        } else {
            node.style("opacity", "0");
            link.style("opacity", "0");
            count = 0;
        }
        
    });
    
    node = node
        .data(graph.nodes)
        .enter().append("circle")
        .attr("class", "node")
        .attr("id", function(d){
            return "n_" + d.id;
        })
        .attr("r", 15)
        .style("fill", "red");
    
        btn.onclick = find_path;

        console.log("Длина: " + graph.nodes.length);
        nodes_length = graph.links[graph.links.length-1].source.id+1;
        
        let column = 0;
        let first_y = -1;
        for(let i = 0; i < nodes_length; ++i){
            if(graph.nodes[i] !== undefined){
                if(first_y === -1)
                    first_y = graph.nodes[i].y;
                if(first_y !== graph.nodes[i].y)
                    break;
                    column++;
            }
        }
        
        let row = Math.round(nodes_length / column);
        
        //иницииализация двумерного массива
        let second_array = [column];
        for (let i=0; i <= row; i++){
            second_array[i] = new Array();
            for (let j=0; j<=column; j++){
                second_array[i][j]=0;
            }
         }
        
        
        
        //массив вершин, которые существуют!
        let exist_array = new Array(nodes_length).fill(1);
        for(let i = 0; i < nodes_length; ++i) {
            if(find(i)){
                exist_array[i] = 0;
            } else { exist_array[i] = 1; }
        }
        console.log(exist_array);
        //заполняем двумерный массив данными!
        for(let i = 0; i <= row; ++i) {
            for(let j = 0; j <= column; ++j) {
                second_array[i][j] = exist_array[i*column + j];
            }
        }
    
        //функция сверки id узла и его положения в JSON
        function find(id_node) {
            for(let i = 0; i < graph.nodes.length; ++i)
                    if(graph.nodes[i].id === id_node)
                             return graph.nodes[i];
            
            return false;
        }
    
        
        //ЗДЕСЬ КОД ОПРЕДЕЛЕНИЯ КООРДИНАТ КЛИКА
        function coordinates(current_x, current_y) {
            let offset; //мб понадобится
            let nodes_coordinates = [];
            
            let dif = 100000;
            let cur_x = 0;
            let temp;
            for(let i = 0; i < nodes_length; ++i) {
                if(find(i)){
                if(Math.abs(current_x - find(i).x) < dif){
                 dif = Math.abs(current_x - find(i).x);
                 temp = find(i).id;
                }else {
                    cur_x = temp;
                    break;
                    }
                }
            }
            cur_y = 0;
            let counter = 1;
            dif = 100000;
            
            for(let i = 0; i < nodes_length; ++i) {
                if(find(i) && (find(i).x === graph.nodes[cur_x].x)){
                    if(Math.abs(current_y - find(i).y) <= dif) {
                        temp = find(i).id;
                        dif = Math.abs(current_y - find(i).y);
                    } else {
                        return temp;
                    }
                }
            }
        }
        
        
        
        
        
        
        
        
        
        //
        
        
        function find_path() {
            if(first===0)
                    return alert("Выберите точки!");
                    
        
            var grid = new PF.Grid(second_array);
                console.log(grid);
    
            var finder = new PF.AStarFinder({
                allowDiagonal :  true ,
           });
           
           
            start_x = first % column;
            start_y = Math.floor(first / column);
            
            end_x = second % column;
            end_y = Math.floor(second / column);
            
            
            var path_matrix = finder.findPath(start_x, start_y, end_x, end_y, grid);
            
            console.log("путь в матричной форме: " );
            console.log(path_matrix);
            let path = [path_matrix.length];
            
            if(path_matrix.length === 0){
                alert("пути не существует!");
            } else {
            for(let i = 0; i < path_matrix.length; ++i) { 
                path[i] = path_matrix[i][0] + column * path_matrix[i][1];   
            } 
            
            var x = d3.scaleLinear();
            var y = d3.scaleLinear();
    
            //Построение линии на основе найденного пути
            var line = d3.line()
             .curve(d3.curveNatural)
              .x(function(d) {
                  return x(find(d).x)})
              .y(function(d) {
                  return y(find(d).y)});
            
            // анимация линии
            var path_animation = svg.append("path")
                .attr("d", line(path))
                .attr("stroke", "red")
                .attr("stroke-width", "5")
                .attr("stroke-linecap","round")
                .attr("fill", "none");
        
            var totalLength = path_animation.node().getTotalLength();
        
            path_animation
                .attr("stroke-dasharray", totalLength + " " + totalLength)
                .attr("stroke-dashoffset", totalLength)
                .transition()
                .duration(function(d) {
                    return totalLength*5;
                })
                .ease(d3.easeLinear)
                .attr("stroke-dashoffset", 0); 
            }
          }

    function ticked() {
    link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    node.attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; })
        
    }
