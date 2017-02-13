let ram = {};


ram.process_custom_json = function(data){
	this._parsing=true;
	data = data.responseText || data;
	if (typeof data == "string"){
		eval("dhtmlx.temp="+data+";");
		data = dhtmlx.temp;
	}
console.log(data);
	//parse, similar to the xml based sample
	if (data.data)
		data = data.data;
	for (let i = 0; i < data.length; i++){
		let row = data[i];
		let id  = row.id||(i+1);
		this.rowsBuffer.push({
				idd: id,
				data: row,
				_parser: this._process_js_row,
				_locator: this._get_js_data
		});
		
		this.rowsAr[id]=data[i];
	}

	this.render_dataset();
	this._parsing=false;
};


ram.initGrid = function(grid, config) {
	grid.setImagePath("js/dhtmlxGrid_v50_std/codebase/imgs/");
	grid.setImagePath("js/dhtmlxGrid_v50_std/skins/web/imgs/dhxgrid_web/");
	grid.setHeader(config.header);							//the headers of columns  
	grid.setColumnIds(config.columnIds);					//the field names of columns  
	grid.setInitWidths(config.initWidths); 	   				//the widths of columns  
	grid.setColAlign(config.colAligns);       				//the alignment of columns   
	grid.setColTypes(config.colTypes);                		//the types of columns  
	grid.setColSorting(config.colSorting);          		//the sorting types   
	grid.init();      										//finishes initialization and renders the grid on the page 

	grid._process_custom_json = this.process_custom_json

	// fetch(config.source)
	// 	.then(response=>response.json())
	// 	.then(data=>grid.load(data,"custom_json"))
	// 	// .then(data => console.log(data)) 

	grid.load(config.source,"custom_json");

};

ram.initRoomsGrid = function() {
	let rooms_table = new dhtmlXGridObject('rooms_table');
	let config = {
		source: "data/meeting_rooms.json",
		header: "Select,Venue,Name,Seats,Booths",
		columnIds: "Selected,Venue,Name,NumberOfSeats,NumberOfBooths",
		initWidths: "45,130,160,45,50",
		colAligns: "center,left,left,right,right",
		colTypes: "ch,ro,ro,ed,ed",
		colSorting: "str,str,int,int"
	}
	this.initGrid(rooms_table, config);

	rooms_table.attachEvent("onCheck", function(rId,cInd,state){
		console.log([rId, cInd, state])
	});
}


ram.init = function() {
	this.initRoomsGrid();
}
