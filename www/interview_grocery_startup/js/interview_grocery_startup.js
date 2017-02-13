var jQuery = jQuery.noConflict(); 

var igs={};

igs.payload = {
					"cfg": {"what": "cost",
							"maxWeight": 10,
							"maxCost": 100,
							"minCals": 14000,
							"minShop": 0.25,
							"total_cost": 0,
							"food":  [["ham",650, 4],
										["lettuce",70,1.5],
										["cheese",1670,5],
										["tuna",830,20],
										["bread",1300,1.20]]
						}
				};


igs.fillGroceryTable = function() {
	var foods = this.payload.cfg.food;
	var groceryTable=jQuery('#grocerytable tbody');
	foods.forEach(function(food,i){
		var row = '<tr>';
		food.forEach(function(prop,j){
			myClass='';
			tangleClass='';
			dataVar='';
			dataMin=0;
			dataMax=100000;
			dataStep=1;
			switch(j){
				case 0:
					myClass='food';
					break;
				case 1:
					myClass='calories';
					tangleClass='TKAdjustableNumber';
					dataStep=10;
					break;
				case 2:
					myClass='price';
					tangleClass='TKAdjustableNumber';
					dataStep=0.25;
					break;
				default:
					myClass='';
			}
			row+='<td class="'+myClass+'" >'+
					'<span class="' + tangleClass + '"' +
					//data-var is food_row_column of the table 
					'data-var="food_'+i+'_'+j+'" '+
					'data-min="'+dataMin+'" '+
					'data-max="'+dataMax+'" '+
					'data-step="'+dataStep+'" '+
					// 'data-format="%.0f" '+
					'>'+
					// ''+prop+
					+'</span>'+
					'</td>';
		})
		row+='</tr>'
		groceryTable.append(row);
	});

	igs.tangleInit();
};


igs.getFoodRowCol = function(pointer) {
	// return second and third element of pointer
	return pointer.split('_').splice(1);
};

igs.getCfgValue = function(key) {
	return this.payload.cfg[key];
}

igs.setCfgValue = function(key,value){
	this.payload.cfg[key]=value;
}

igs.getFoodValue = function(pointer) {
	var coord=getFoodRowCol(pointer);
	return this.payload.cfg.food[coord[0]][coord[1]];
};

igs.setFoodValue = function(pointer, value) {
	var coord=this.getFoodRowCol(pointer);
	this.payload.cfg.food[coord[0]][coord[1]] = value;
};

igs.to = true;
igs.throttle = function(func, delay){
    if (igs.to) {
    	window.clearTimeout(igs.to);
    }
    igs.to = window.setTimeout(func, delay);
};


igs.tangleInit = function() {
	jQuery('#grocerytable td span').text('');
	var tangle = new Tangle (document.getElementById("problem"), {
	    initialize: function () {
	    	var that = this;
	    	that.maxWeight = igs.getCfgValue('maxWeight');
	    	that.maxCost = igs.getCfgValue('maxCost');
	    	that.minCalsDay = igs.getCfgValue('minCals')/7;
	    	that.minShop = igs.getCfgValue('minShop');
	    	that.minShopOunces = that.minShop*16;
	    	igs.payload.cfg.food.forEach(function(item, i){
	    		item.forEach(function(prop, j){
	    			that['food_'+i+'_'+j]=prop;
	    		});
	    	});
	    },
	    update: function () {
	    	var that = this;
	    	that.minShop = that.minShopOunces/16;
	    	that.minCals = that.minCalsDay*7;
	    	igs.setCfgValue('maxWeight', that.maxWeight);
	    	igs.setCfgValue('maxCost', that.maxCost);
	    	igs.setCfgValue('minCals', that.minCals);
	    	igs.setCfgValue('minShop', that.minShop);
	    	igs.payload.cfg.food.forEach(function(item, i){
	    		item.forEach(function(prop, j){
	    			igs.setFoodValue('food_'+i+'_'+j, that['food_'+i+'_'+j]);
	    		});
	    	});
	    	igs.throttle(igs.post, 500);
	    }
	});
};

igs.setTotalCost = function(data) {
	var totalCost = 0;
	igs.payload.cfg.food.forEach(function(item){
		totalCost+=item[2] * data['variables'][item[0]];
	});
	console.log(totalCost);
	data['total_cost'] = totalCost;
	return data;
};

igs.clearAnswerTable = function(data){
	var variablestable=jQuery('#variablestable');
	variablestable.find('tbody').html('');
	variablestable.removeClass('green red');
	if (data['result_status']==='optimal answer') {
		variablestable.addClass('green');
	} else {
		variablestable.addClass('red');
	}
};

igs.fillAnswerTable = function(data) {

	igs.clearAnswerTable(data);

	var variablestable=jQuery('#variablestable tbody');

	if (data['variables']){
		igs.setTotalCost(data);
		Object.keys(data['variables']).forEach(function(variable){
			data['variables'][variable] = (+data['variables'][variable]).toFixed(2);
			variablestable.append('<tr><td>'+variable+'</td><td>'+data['variables'][variable]+'</td></tr>');
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

igs.post = function() {
	jQuery('#answer .dimmer').addClass('active');

    jQuery.ajax({
      type: "POST",
      url: "/gunicorn/igsapi",
      dataType: "json",
      data: JSON.stringify(igs.payload),

      error:function (xhr, ajaxOptions, thrownError){
      	console.log(thrownError);
      },

      success:function(data, textStatus, jqXHR){
        console.log(data);
        igs.fillAnswerTable(data);
      }
    });
    return false;
};


jQuery(document).ready(function(){
	igs.post();
	igs.fillGroceryTable();

	jQuery('#answer').hide();

	jQuery("#get_answer button").click(function(evt){
		jQuery('#get_answer').hide();
		jQuery('#answer').show();
	});

	jQuery("#goal input[type='radio']").change(function(value){
		igs.payload.cfg.what = jQuery(this).val();
		igs.post();
	});

});
