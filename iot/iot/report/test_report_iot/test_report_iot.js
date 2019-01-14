// Copyright (c) 2016, JETFOX - PT.Perkasa Jaya Kirana and contributors
// For license information, please see license.txt
/* eslint-disable */
frappe.query_reports["Test Report IOT"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname":"node",
			"label": __("Node"),
			"fieldtype": "Link",
			"options": "Node",
			"get_query": function() {
				var node = frappe.query_report.get_filter_value('signal');
				return {
					"doctype": "Node"

				}
			}
		},{
			"fieldname":"signal",
			"label": __("Signal"),
			"fieldtype": "MultiSelect",
			get_data: function() {
				let node = $(":input[data-fieldname='node']").val()
				console.log('node : ' + node)
				if (!node)
					return
				// var projects = frappe.query_report.get_filter_value("project") || "";

				// const values = projects.split(/\s*,\s*/).filter(d => d);
				// const txt = projects.match(/[^,\s*]*$/)[0] || '';
				let data = [];

				frappe.call({
					type: "GET",
					method:'iot.iot.getSignalList',
					async: false,
					no_spinner: true,
					args: {
						'node_id': node
					},
					callback: function(r) {
						if(r){
							for(let i=0; i < r.message.length; i++){
								data.push(r.message[i].ip+'.'+r.message[i].label)
							}
						}
						if (!r.exc) {
							// code snippet
						}
					}
				});
				return data;
			}
		},
		// {
		// 	"fieldname": "machine",
		// 	"label": __("Item Group"),
		// 	"fieldtype": "Data"
		// },
		// {
		// 	"fieldname":"location",
		// 	"label": __("location"),
		// 	"fieldtype": "Data"
		// },
		// {
		// 	"fieldname": "item_code",
		// 	"label": __("Item"),
		// 	"fieldtype": "Link",
		// 	"width": "80",
		// 	"options": "Item",
		// 	"get_query": function() {
		// 		return {
		// 			query: "erpnext.controllers.queries.item_query"
		// 		}
		// 	}
		// },
	],
	get_chart_data: function(columns, result) {

		// return {
		// 		data: {
		// 			labels: result.map(d => d[0]),
		// 			datasets: [{
		// 				name: 'Machine 1',
		// 				values: result.map(d => d[1])
		// 			},
		// 			{
		// 				name: 'Machine 2',
		// 				values: result.map(d => d[2])
		// 			}]
		// 		},
		// 		type: 'bar',
		// 	}
		// }
		return {
			data: {
				labels: result.map(d => d[0]),
				datasets: [{
					name: 'Shift 1',
					values: result.map(d => d[1])
				},
				{
					name: 'Shift 2',
					values: result.map(d => d[2])
				},
				{
					name: 'Shift 3',
					values: result.map(d => d[3])
				}]
			},
			type: 'bar',
		}
	}
}