"use strict";
var jQuery = jQuery.noConflict(); 

var roomAssignmentsWeek={};

roomAssignmentsWeek.payload = {
			'cfg':  { 'what': 'space',
			'rooms': [['I',71],
					['II',60],
					['III',198],
					['IV',61]],
			'meetings':  [[1,'UNHCR', 50],
							[2,'Town Hall', 150],
							[3,'UNCTAD', 68],
							[4,'CAT', 15],
							[5,'CERD', 70]],
			'schedule':	[[1, [[1,'UNHCR', 1],[2,'Town Hall', 1],[3,'UNCTAD', 0],[4,'CAT', 0],[5,'CERD', 0]]],
						 [2, [[1,'UNHCR', 1],[2,'Town Hall', 1],[3,'UNCTAD', 1],[4,'CAT', 1],[5,'CERD', 0]]],
						 [3, [[1,'UNHCR', 1],[2,'Town Hall', 0],[3,'UNCTAD', 1],[4,'CAT', 1],[5,'CERD', 1]]],
						 [4, [[1,'UNHCR', 1],[2,'Town Hall', 0],[3,'UNCTAD', 1],[4,'CAT', 1],[5,'CERD', 1]]],
						 [5, [[1,'UNHCR', 1],[2,'Town Hall', 0],[3,'UNCTAD', 1],[4,'CAT', 0],[5,'CERD', 1]]]]
			}
};


roomAssignmentsWeek.fillRoomsTable = function() {
	var rooms = this.payload.cfg.rooms;
	var roomsTable=jQuery('#rooms_table tbody');
	rooms.forEach(function(room,i){
		var row = '<tr>';

		room.forEach(function(prop,j){
			var config = {
				myClass: '',
				tangleClass: '',
				dataVar: 'rooms',
				dataMin: 0,
				dataMax: 100000,
				dataStep: 1,
				value: prop		
			};
			switch(j){
				case 0:
					config.myClass='room';
					break;
				case 1:
					config.myClass='capacity';
					config.tangleClass='TKAdjustableNumber';
					config.dataStep=5;
					break;
				default:
					config.myClass='';
			}
			row+=roomAssignmentsWeek.getCellHTML(config, i, j);
		});
		row+='</tr>';
		roomsTable.append(row);
	});

};

roomAssignmentsWeek.fillMeetingsTable = function() {
	var meetings = this.payload.cfg.meetings;
	var meetingsTable=jQuery('#meetings_table tbody');

	meetings.forEach(function(meeting,i){
		var row = '<tr>';

		meeting.forEach(function(prop,j){
			var config = {
				myClass: '',
				tangleClass: '',
				dataVar: 'meetings',
				dataMin: 0,
				dataMax: 100000,
				dataStep: 1,
				value: prop
			};
			switch(j){
				case 0:
					config.myClass='meeting_number';
					break;
				case 1:
					config.myClass='name';
					break;
				case 2:
					config.myClass='attendance';
					config.tangleClass='TKAdjustableNumber';
					config.dataStep=5;
					break;
				default:
					config.myClass='';
			}
			row+=roomAssignmentsWeek.getCellHTML(config, i, j);
		});
		row+='</tr>';
		meetingsTable.append(row);
	});

};


roomAssignmentsWeek.fillScheduleTable = function() {
	var schedule = this.payload.cfg.schedule;
	var meetings = this.payload.cfg.meetings;

	var scheduleTable=jQuery('#schedule_table thead');
	scheduleTable.find('th.meetings').attr('colspan',meetings.length);

	//client headers
	var row = '<tr>';
	row+='<th>Days</th>';
	meetings.forEach(function(meeting){
		row += '<th class="center aligned">' + meeting[1] + '</th>';
	});
	row+='</tr>';
	scheduleTable.append(row);

	scheduleTable=jQuery('#schedule_table tbody');

	schedule.forEach(function(dayschedule, h){
		var row = '<tr>';
		row += '<td>'+dayschedule[0]+'</td>';
		dayschedule[1].forEach(function(meeting, i){
			meeting.forEach(function(prop, j){
				var config = {
					myClass: '',
					tangleClass: '',
					dataVar: 'schedule',
					dataMin: 0,
					dataMax: 100000,
					dataStep: 1,
					value: prop
				};
				switch(j){
					case 0:
						config.myClass='meeting_number';
						break;
					case 1:
						config.myClass='name';
						break;
					case 2:
						config.myClass='schedule center aligned';
						config.tangleClass='checkbox';
						break;
					default:
						config.myClass='';
				}
				if (j===2){
					//show only the checkboxes
					row+=roomAssignmentsWeek.getCellHTML(config, i, j, h);
				}
			});
		});
		row+='</tr>';
		scheduleTable.append(row);
	});

};

roomAssignmentsWeek.getCellHTML = function(c, i, j, h) {
	var rtn='';
	h = (h ? h : 0);
	rtn +='<td class="'+c.myClass+'" >';
	if (c.tangleClass==='TKAdjustableNumber') {
		rtn+='<div class="ui tiny input">' +
			'<input class="update-trigger" type="text" ' + 
			'data-var="'+[c.dataVar,i,j,h].join('_')+'" '+
			'value="'+c.value+'"' +
			'/>' +
			'</div>';
	} else if (c.tangleClass==='checkbox') {
		rtn+='<div class="ui checked checkbox">'+
			  '<input class="update-trigger" type="checkbox" ' +
			  (c.value===1 ? 'checked=""': '') +
			  'data-var="'+[c.dataVar,i,j,h].join('_')+'" '+
			  '/>' +
			  '<label></label>'+
			 '</div>';
	} else {
		rtn += c.value;
	}
	rtn += '</td>';

	return rtn;
	/*
	return '<td class="'+c.myClass+'" >'+
			'<span class="' + c.tangleClass + '"' +
			//data-var is dataVar_row_column of the table 
			'data-var="'+[c.dataVar,i,j].join('_')+'" '+
			'data-min="'+c.dataMin+'" '+
			'data-max="'+c.dataMax+'" '+
			'data-step="'+c.dataStep+'" '+
			// 'data-format="%.0f" '+
			'>'+
			'</span>'+
			'</td>';
	*/
};


roomAssignmentsWeek.getRowCol = function(pointer) {
	// return second and third element of pointer
	return pointer.split('_').splice(1);
};

roomAssignmentsWeek.getCfgValue = function(key) {
	return this.payload.cfg[key];
};

roomAssignmentsWeek.setCfgValue = function(key,value){
	this.payload.cfg[key]=value;
};

roomAssignmentsWeek.getValue = function(cfgItem, pointer) {
	var coord=this.getRowCol(pointer);
	return this.payload.cfg[cfgItem][coord[0]][coord[1]];
};

roomAssignmentsWeek.setValue = function(cfgItem, pointer, value) {
	if (typeof value !== 'undefined'){

		var coord=this.getRowCol(pointer);
		if (!this.payload.cfg[cfgItem][coord[0]]){
			this.payload.cfg[cfgItem][coord[0]]=[];
		}
		if (!isNaN(value)){
			value = +value;
		}
		if (cfgItem==='schedule') {
			this.payload.cfg[cfgItem][coord[2]][1][coord[0]][coord[1]] = value;
		} else {
			this.payload.cfg[cfgItem][coord[0]][coord[1]] = value;
		}
		// console.log(this.payload);
	}
	return false;
};

roomAssignmentsWeek.to = true;
roomAssignmentsWeek.throttle = function(func, delay){
    if (roomAssignmentsWeek.to) {
    	window.clearTimeout(roomAssignmentsWeek.to);
    }
    roomAssignmentsWeek.to = window.setTimeout(func, delay);
};


roomAssignmentsWeek.tangleInit = function() {
	/*
	this.tangle = new Tangle (document.getElementById('problem'), {
	    initialize: function () {
	    	var that = this;
	    	//go through the array of the configuration 
	    	Object.keys(roomAssignmentsWeek.payload.cfg).forEach(function(key){
	    		//if item is an array
	    		if (roomAssignmentsWeek.isArray(roomAssignmentsWeek.payload.cfg[key])) {
	    			//go through the array initializing variables
			    	roomAssignmentsWeek.payload.cfg[key].forEach(function(item, i){
			    		item.forEach(function(prop, j){
			    			that[[key,i,j].join('_')]=prop;
			    		});
			    	});	    			
	    		}
	    	});
	    },
	    update: function(){
	    	var that = this;
			//go through the array of the configuration 
			Object.keys(roomAssignmentsWeek.payload.cfg).forEach(function(key){
				//if item is an array
				if (roomAssignmentsWeek.isArray(roomAssignmentsWeek.payload.cfg[key])) {
					//go through the array setting variables
			    	roomAssignmentsWeek.payload.cfg[key].forEach(function(item, i){
			    		item.forEach(function(prop, j){
			    			roomAssignmentsWeek.setValue(key, [key,i,j].join('_'), that[[key,i,j].join('_')]);
			    		});
			    	});
				}
			});
			roomAssignmentsWeek.throttle(roomAssignmentsWeek.post, 500);
	    }
	});
	*/
};


roomAssignmentsWeek.isArray = function(variable){
	return (Object.prototype.toString.call( variable ) === '[object Array]');
};


roomAssignmentsWeek.clearAnswerTable = function(data){
	var answerTable=jQuery('#answer_table');
	answerTable.find('thead tr:last-child').html('');
	answerTable.find('tbody').html('');
	answerTable.removeClass('green red');
	if (data['result_status']==='optimal answer') {
		answerTable.addClass('green');
	} else {
		answerTable.addClass('red');
	}
};

roomAssignmentsWeek.fillAnswerTable = function(data) {

	roomAssignmentsWeek.clearAnswerTable(data);


	var rooms = this.payload.cfg.rooms;

	var answerTable=jQuery('#answer_table thead');
	answerTable.find('th.rooms').attr('colspan',rooms.length);

	//client headers
	var row = '<tr>';
	row+='<th>Days</th>';
	rooms.forEach(function(room){
		row += '<th class="center aligned">' + room[0] + '</th>';
	});
	row+='</tr>';
	answerTable.append(row);

	answerTable=jQuery('#answer_table tbody');

	if (data['variables_display']){
		Object.keys(data['variables_display']).forEach(function(variable){ 
			var row = '<tr>';
			row += '<td>'+variable+'</td>';
			rooms.forEach(function(room){
				// console.log( data['variables_display'][variable] );
				var roomMeeting = (data['variables_display'][variable][room[0]] ? data['variables_display'][variable][room[0]] : '');
				row+='<td>'+roomMeeting+'</td>';
			});
			row += '</tr>';
			answerTable.append(row);
		});
	}

	Object.keys(data).forEach(function(key){
		var value;
		if (isNaN(data[key])) {
			value = data[key]
		} else {
			//it's a number (perhaps?)
			value = (+data[key]).toFixed(2)
		}
		jQuery('#'+key).text(value);
	});
	jQuery('#answer .dimmer').removeClass('active');
};


roomAssignmentsWeek.addInput = function(tableName) {
	var inputHTML = '<tr class="ui tiny form">';
	var table = jQuery('#'+tableName);
	var key = tableName.substring(0,tableName.indexOf('_'))
	var rowCount = table.find('tr').length - 1 ;
	if (tableName==='rooms_table'){
		inputHTML +='<td><div class="input field"><input type="text" data-var="'+key+'_'+rowCount+'_0"/></div></td>'+
					'<td><div class="input field"><input class="update-trigger" type="text" data-var="'+key+'_'+rowCount+'_1"/></div></td>';
	}

	else if (tableName==='meetings_table'){
		inputHTML +='<td><div class=""><span data-var="'+key+'_'+rowCount+'_0"></span></div></td>'+
					'<td><div class="input field"><input type="text" data-var="'+key+'_'+rowCount+'_1"/></div></td>'+
					'<td><div class="input field"><input class="update-trigger" type="text" data-var="'+key+'_'+rowCount+'_2"/></div></td>';
	}
	inputHTML += '</tr>';
	table.append(inputHTML); 

	table.find(".update-trigger").change(function(){ roomAssignmentsWeek.fieldChange(this);});

	table.find(".update-trigger").keydown(roomAssignmentsWeek.fieldKeyDown);

	return false;
};

roomAssignmentsWeek.fieldChange = function(el) {

	jQuery(el).addClass('changed');
	var variable = jQuery(el).data('var');
	// console.log(variable);
	var key = variable.substring(0,variable.indexOf('_'));
    jQuery('#'+key+'_table input').each(function(i, field){
    	var item = jQuery(this);
    	var pointer = item.data('var');
    	var value = item.val();
    	if (item.attr('type')==='checkbox'){
    		value = (item.is(':checked') ? 1 : 0);
    	} 
    	roomAssignmentsWeek.setValue(key, pointer, value);
    });
    roomAssignmentsWeek.throttle(roomAssignmentsWeek.post, 500);
}

roomAssignmentsWeek.fieldKeyDown = function(evt) {
	if ( event.which == 13 ) {
		jQuery('#answer').show();
		jQuery('#get_answer').hide();
  	} else {
  		jQuery('#answer').hide();
		jQuery('#get_answer').show();
  	}
};

roomAssignmentsWeek.post = function() {

	jQuery('#answer .dimmer').addClass('active');
	// console.log(roomAssignmentsWeek.payload);
    jQuery.ajax({
      type: "POST",
      url: "/gunicorn/room_assignments_week_api",
      dataType: "json",
      data: JSON.stringify(roomAssignmentsWeek.payload),

      error:function (xhr, ajaxOptions, thrownError){
      	console.log(thrownError);
      },

      success:function(data, textStatus, jqXHR){
        // console.log(data);
        roomAssignmentsWeek.fillAnswerTable(data);
      }
    });
    return false;
};


jQuery(document).ready(function(){
	jQuery('#answer').hide();

	roomAssignmentsWeek.fillRoomsTable();
	roomAssignmentsWeek.fillMeetingsTable();
	roomAssignmentsWeek.fillScheduleTable();
	// roomAssignmentsWeek.tangleInit();
	roomAssignmentsWeek.throttle(roomAssignmentsWeek.post, 500);

	jQuery('.update-trigger').change(function(){ roomAssignmentsWeek.fieldChange(this);});
	jQuery(".update-trigger").keydown(roomAssignmentsWeek.fieldKeyDown);


	jQuery("#goal input[type='radio']").change(function(value){
		roomAssignmentsWeek.payload.cfg.what = jQuery(this).val();
		roomAssignmentsWeek.post();
	});

	jQuery("#get_answer button").click(function(evt){
		jQuery('#get_answer').hide();
		jQuery('#answer').show();
	});

	jQuery(".add-input").click(function(evt){
		roomAssignmentsWeek.addInput(jQuery(this).data('target'));
	});

});
