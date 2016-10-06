"use strict";
var jQuery = jQuery.noConflict(); 

var roomAssignments={};

roomAssignments.payload = {
					'cfg':  {'what': 'usage',
							'rooms': [['I',71],
												['II',22],
												['III',198],
												['IV',61]],
							'meetings':  [[1,'UNHCHR', 50],
														[2,'Town Hall', 150],
														[3,'UNCTAD', 68],
														[4,'CAT', 15]]
							}
						};


roomAssignments.fillRoomsTable = function() {
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
				dataStep: 1		
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
			row+=roomAssignments.getCellHTML(config, i, j);
		});
		row+='</tr>';
		roomsTable.append(row);
	});

};

roomAssignments.fillMeetingsTable = function() {
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
				dataStep: 1		
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
			row+=roomAssignments.getCellHTML(config, i, j);
		});
		row+='</tr>';
		meetingsTable.append(row);
	});

};

roomAssignments.getCellHTML = function(c, i, j) {
	return '<td class="'+c.myClass+'" >'+
			'<span class="' + c.tangleClass + '"' +
			//data-var is dataVar_row_column of the table 
			'data-var="'+[c.dataVar,i,j].join('_')+'" '+
			'data-min="'+c.dataMin+'" '+
			'data-max="'+c.dataMax+'" '+
			'data-step="'+c.dataStep+'" '+
			// 'data-format="%.0f" '+
			'>'+
			// ''+prop+
			'</span>'+
			'</td>';
};


roomAssignments.getRowCol = function(pointer) {
	// return second and third element of pointer
	return pointer.split('_').splice(1);
};

roomAssignments.getCfgValue = function(key) {
	return this.payload.cfg[key];
};

roomAssignments.setCfgValue = function(key,value){
	this.payload.cfg[key]=value;
};

roomAssignments.getValue = function(cfgItem, pointer) {
	var coord=this.getRowCol(pointer);
	return this.payload.cfg[cfgItem][coord[0]][coord[1]];
};

roomAssignments.setValue = function(cfgItem, pointer, value) {
	var coord=this.getRowCol(pointer);
	this.payload.cfg[cfgItem][coord[0]][coord[1]] = value;
};

roomAssignments.to = true;
roomAssignments.throttle = function(func, delay){
    if (roomAssignments.to) {
    	window.clearTimeout(roomAssignments.to);
    }
    roomAssignments.to = window.setTimeout(func, delay);
};


roomAssignments.tangleInit = function() {
	var tangle = new Tangle (document.getElementById('problem'), {
	    initialize: function () {
	    	var that = this;
	    	//go through the array of the configuration 
	    	Object.keys(roomAssignments.payload.cfg).forEach(function(key){
	    		//if item is an array
	    		if (roomAssignments.isArray(roomAssignments.payload.cfg[key])) {
	    			//go through the array initializing variables
			    	roomAssignments.payload.cfg[key].forEach(function(item, i){
			    		item.forEach(function(prop, j){
			    			that[[key,i,j].join('_')]=prop;
			    		});
			    	});	    			
	    		}
	    	});
	    },
	    update: function () {
	    	var that = this;
	    	//go through the array of the configuration 
	    	Object.keys(roomAssignments.payload.cfg).forEach(function(key){
	    		//if item is an array
	    		if (roomAssignments.isArray(roomAssignments.payload.cfg[key])) {
	    			//go through the array setting variables
			    	roomAssignments.payload.cfg[key].forEach(function(item, i){
			    		item.forEach(function(prop, j){
			    			roomAssignments.setValue(key, [key,i,j].join('_'), that[[key,i,j].join('_')]);
			    		});
			    	});	    			
	    		}
	    	});
	    	roomAssignments.throttle(roomAssignments.post, 500);
	    }
	});
};

roomAssignments.isArray = function(variable){
	return (Object.prototype.toString.call( variable ) === '[object Array]');
};


roomAssignments.clearAnswerTable = function(data){
	var answerTable=jQuery('#answer_table');
	answerTable.find('tbody').html('');
	answerTable.removeClass('green red');
	if (data['result_status']==='optimal answer') {
		answerTable.addClass('green');
	} else {
		answerTable.addClass('red');
	}
};

roomAssignments.fillAnswerTable = function(data) {

	roomAssignments.clearAnswerTable(data);

	var answerTable=jQuery('#answer_table tbody');
	if (data['variables_display']){
		Object.keys(data['variables_display']).forEach(function(variable){ 
			answerTable.append('<tr><td>'+variable+'</td><td>'+data['variables_display'][variable]+'</td></tr>');
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

roomAssignments.post = function() {

	jQuery('#answer .dimmer').addClass('active');

    jQuery.ajax({
      type: "POST",
      url: "http://localhost:18000/room_assignments_api",
      dataType: "json",
      data: JSON.stringify(roomAssignments.payload),

      error:function (xhr, ajaxOptions, thrownError){
      	console.log(thrownError);
      },

      success:function(data, textStatus, jqXHR){
        console.log(data);
        roomAssignments.fillAnswerTable(data);
      }
    });
    return false;
};


jQuery(document).ready(function(){
	jQuery('#answer').hide();

	roomAssignments.fillRoomsTable();
	roomAssignments.fillMeetingsTable();
	roomAssignments.tangleInit();

	jQuery("#goal input[type='radio']").change(function(value){
		roomAssignments.payload.cfg.what = jQuery(this).val();
		roomAssignments.post();
	});

	jQuery("#get_answer button").click(function(evt){
		jQuery('#get_answer').hide();
		jQuery('#answer').show();
	});

});
