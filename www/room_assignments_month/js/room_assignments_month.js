let ram = {};

ram.roomData=[];
ram.meetingData=[];
ram.accordionRoomsMeetings = {};

ram.process_custom_json = function(data){
	this._parsing=true;
	data = data.responseText || data;

	if (typeof data == "string"){
		eval("dhtmlx.temp="+data+";");
		data = dhtmlx.temp;
	}
	//console.log(data);
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

	grid.parse(config.source,"custom_json");

};

ram.initDataProcessor = function(grid) {
	let dp = new dataProcessor("data/connector.php");
	dp.init(grid);
	dp.setTransactionMode("REST");
}

ram.processOnCheck = function(datasetName,columnIds,rId,cInd,state){
	const selected = columnIds.split(',')[cInd];
	ram[datasetName][rId][selected]=state*1;
	console.log(ram[dataSetName][rId]);
}

ram.initRoomsGrid = function() {
	let grid = new dhtmlXGridObject('rooms_table');
	// let grid = this.accordionRoomsMeetings.cells("rooms_table").attachGrid();
	let config = {
		source: this.roomData,
		header: "Select,Venue,Name,Seats,Booths",
		columnIds: "Selected,Venue,Name,NumberOfSeats,NumberOfBooths",
		initWidths: "45,130,160,45,50",
		colAligns: "center,left,left,right,right",
		colTypes: "ch,ro,ro,ed,ed",
		colSorting: "int,str,str,int,int"
	}
	this.initGrid(grid, config);

	grid.attachEvent("onCheck", function(rId,cInd,state){
		processOnCheck('roomData',config.columnIds,rId,cInd,state);
	});

	this.initDataProcessor(grid);

	return grid;
}

ram.initMeetingsGrid = function() {
	let grid = new dhtmlXGridObject('meetings_table');
	// let grid = this.accordionRoomsMeetings.cells("meetings_table").attachGrid();
	let config = {
		source: this.meetingData,
		header: "Select,Date,Client,Title,Participants,Time Slot",
		columnIds: "SELECTED,MEETING_DATE,ORGAN_ACRONYM,MEETING_TITLE,MEETING_PARTICIPANTS,TIME_SLOT",
		initWidths: "45,100,300,300,60,50",
		colAligns: "center,right,left,left,right,center",
		colTypes: "ch,ro,ro,ro,ed,ed",
		colSorting: "date,str,str,int,int"
	}
	this.initGrid(grid, config);

	grid.attachEvent("onCheck", function(rId,cInd,state){
		processOnCheck('meetingData',config.columnIds,rId,cInd,state);
	});

	this.initDataProcessor(grid);

	return grid;
}

ram.init = function() {
	// $('.ui.accordion').accordion('exclusive', false);

	
	// this.accordionRoomsMeetings = new dhtmlXAccordion({
	// 	parent: "accordion_rooms_meetings",
	// 	multi_mode: true,
	// 	items: [
	// 		{id: "rooms_table", text: "Rooms", height:"*"},
	// 		{id: "meetings_table", text: "Meetings", open:false, height:"*"}
	// 	]
	// });

	$('.menu .item').tab();
	
	fetch('data/meeting_rooms.json')
	.then(response=>response.json())
	.then(data=>{
		this.roomData = data;
		let grid = this.initRoomsGrid();
	});
	fetch('data/meetings.json')
	.then(response=>response.json())
	.then(data=>{
		this.meetingData = data;
		let grid = this.initMeetingsGrid();
	});


}
