//reorder after search?
var default_order = $('#left-list > .list-group-item').map(function () {
	return this.id;
}).get();
var new_order;


//search function
$(function search() {
	$("#search_button").click(function(){
		var search_options = [];
        $.each($("input[type=checkbox][name=search_options]:checked"), function(){
            search_options.push($(this).val());
        });
		if ($("#search_box").val().length>0){
		$.getJSON('/search_handler',{
			Search_string: $("#search_box").val(), Search_options: search_options.join(",")
			},
			function(data) {
				$("#left-list > .list-group-item").show();
				new_order = data.result;
				$("#left-list > .list-group-item").hide();
				new_order.reverse().forEach(function(item){
					$("#left-list > .list-group-item#"+item).show();
					$("#left-list > .list-group-item:first").before($("#left-list > .list-group-item#"+item));
					});
			});
		}
		else{
			default_order.forEach(function(item){
				$("#left-list > .list-group-item:last").after($("#left-list > .list-group-item#"+item));	
			})
			$("#left-list > .list-group-item").show();
		};
		return false;
		});
});

//enter in search textarea
$('#search_box').on('keyup', function(e) {
    if (e.keyCode === 13) {
        $('#search_button').click();
    }
});
    
//$(".list-group-item").click(function(){
//    if($(this).closest("#center-list").length>0){
//        task_recieve($(this).attr('id'));
//    };
//    return false;
//});

//recieve task data from server
function task_recieve(task_id){	
	$("#loader").show();	
	var task_json = null;
	$.getJSON('/get_info',{
			id: task_id
		},
		function(data) {
			$("#right-list > .list-group-item").show();
			task_json = data.result;
			if ($("#Category option").length)
			{
				$(".id").text(task_id);
				$("#Category").html("<option value=\"Web\">Web</option><option value=\"Rev\">Reverse</option><option value=\"HTB\">HTB</option><option value=\"Steg\">Steganography</option><option value=\"Cryp\">Cryptography</option><option value=\"Misc\">Misc</option><option value=\"Joy\">Joy</option><option value=\"PWN\">PWN</option>");
				$("#Name textarea").val(task_json.Name);
				$("#Category option[value="+ task_json.Category +"]").attr("selected","selected");
			}
			else
			{
				$("#Name").html("<div class=\"division\"><div class=\"category\"><p>"+task_json.Category_full+"</p></div><div class=\"text\"><textarea style=\"width:100%;resize:none;overflow:auto\">"+task_json.Name+"</textarea></div></div>");
			}
			$("#Description").html("<textarea style=\"width:100%;resize:none;overflow:auto\">"+task_json.Description+"</textarea>");
			$("#Flag").html("<textarea style=\"width:100%;resize:none;overflow:auto\">"+task_json.Flag+"</textarea>");
			$("#save_button").show();
			expand();
			
		}
	)
	$("#loader").hide();
}


//expand textarea size while typing
function expand(){
	te = document.getElementsByTagName('textarea');
	for (var i = te.length - 1; i >= 0; --i) {
		te[i].addEventListener('keyup', resizeTextarea);
		te[i].style.height = '24px';
		te[i].style.height = te[i].scrollHeight + 12 + 'px';
	}
	function resizeTextarea(ev) {
			this.style.height = '24px';
			this.style.height = this.scrollHeight + 12 + 'px';
	}
};


//set center row height dynamically
function set_center_height() {
    $('#center-list').css("height",$('#left-list').height());
 }
window.onload = set_center_height;


//resize top menu if phone screen or so
function myFunction() {
var x = document.getElementById("myTopnav");
if (x.className === "topnav") {
	x.className += " responsive";
} else {
	x.className = "topnav";
}
}
