/*
$(".alert").delay(4000).slideUp(200, function() {
	$(this).alert('close');
});
*/



function nextTab(){
    var navtabsli = $('#navtabs li');
    for (i=0; i< navtabsli.length; i++) {
	if (navtabsli[i].getAttribute("class") == "active") {
		console.log(i);
		if (navtabsli[i].nextElementSibling == null) {
			navtabsli[0].children[0].click();
			return;
		} else {
			navtabsli[i].nextElementSibling.children[0].click();
			return;
		}
	}
    }
};

$(document).ready (function() {
    $(document).keydown( function (e) {
	if (e.ctrlKey && e.keyCode == 39) {
		nextTab();
	}
    });

    $('#leftiframe').contents().on('mouseenter', '.datafield', function () {
    	$(this).find("#datafieldbutton").show();
    }).on('mouseleave', '.datafield', function () {
        $(this).find("#datafieldbutton").hide();
    });
    change_project();
   	setTimeout(function() {
        $(".alert").slideUp(500);
        }, 3000);
 });



function flash(message, category) {

    var message = '<div class="alert alert-'+category+'"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>'+message+'</div>';
    $('#messagebox').append(message);
    setTimeout(function() {

        $(".alert").slideUp(500);
        }, 3000);
 };

function get_dataframerow(object) {
	row = object;
	console.log("blah");

};

function get_dataframefield(object) {
	var field = object;
	var fieldid = field.id.split("_");
	var headfields = field.parentElement.parentElement.previousElementSibling.children[0].children;
	for (i = 0; i<headfields.length; i++) {
		var s_headfield = headfields[i];
		var headclass = s_headfield.getAttribute("class");
		var headcol = headclass.split(" ")[2];
		if (headcol == fieldid[2]) {
			var column_name = s_headfield.innerHTML.split("<")[0];
		}
	}
	
	console.log(column_name + "==" + field.innerHTML);
};

function change_project() {

    var proj_inp = document.getElementById("input_project_select");
    var proj_value = proj_inp.options[proj_inp.selectedIndex].value;
    $.ajax({url:"/change_project?project="+proj_value, type: 'GET', success: function(result){
            console.log("success");
    }});
}

function setProgressbar(progress,totalHits) {

    var progressbar=document.getElementById("downloadprogress");
    var percent = (progress / parseInt(totalHits))*100;
    var percent_output = String(Math.floor(percent)) + "%";
    console.log(percent_output);
    progressbar.style.height = percent_output;
};

function activateControl() {

    var copyrawbutton = document.getElementById("copyrawbutton");
    var downloadbutton = document.getElementById("downloadbutton");

    copyrawbutton.disabled = false;
    downloadbutton.disabled = false;


    flash("Yehaw! Download completed. You can now continue to download.","success");

};


function serveDownload() {

        console.log("serve download");
        $.ajax({url:"/ServeResults?type=download&sessionID="+sessionID, type: 'GET', success: function(result){
            window.open("/static/results/"+result);
    }});
};


function getTableHeadings(iframe){
		
	var col_heads = iframe.getElementsByClassName("col_heading");
	var col_names = [];
	for (i=0; i < col_heads.length; i++){
		col_names.push(col_heads[i].innerHTML);
	}
	return col_names
}


function hideshowCol(checkbox) {
    
	var col = checkbox.value;
	var ifr_con = $("iframe#leftiframe").contents();
	var display_status = ifr_con.find("td:nth-child("+col+")").css("display");
	if (display_status == "none") {
		ifr_con.find("td:nth-child("+col+")").css("display", "table-cell");
		ifr_con.find("th:nth-child("+col+")").css("display", "table-cell");
		}
	else {
		ifr_con.find("td:nth-child("+col+")").css("display", "none");
		ifr_con.find("th:nth-child("+col+")").css("display", "none");
		}

}


function createViewSelect(col_names, viewoptions) {

	for (i=0;i < col_names.length; i++) {
		var input = $('<input/>').attr({type:'checkbox',
				    name:col_names[i], 
			 	    value:i+2,
				    "checked":"checked",
				    id:"tablecheck_"+col_names[i]}).add("<span>"+col_names[i]+"</span>").add("<br>").change(function(e) { hideshowCol(this); }).appendTo(viewoptions);
	}
}

function getIframeDocument(id) {

	var iframe = document.getElementById(id);
	var iframedoc = iframe.contentWindow.document;
	return iframedoc
}

$('#leftiframe').load(function() {

	var viewoptions = document.getElementById("viewoptionsdropdown");
	var lifr_con = getIframeDocument("leftiframe");
	
	col_names = getTableHeadings(lifr_con);
	createViewSelect(col_names, viewoptions);

})

$('#rightiframe').load(function() {

	var viewoptions = document.getElementById("viewoptionsdropdown");
	var lifr_con = getIframeDocument("rightiframe");
	
	col_names = getTableHeadings(lifr_con);
	createViewSelect(col_names, viewoptions);


})


$('#if').load(function() {


    sessionID=document.getElementById("hiddensessionid").innerHTML;
    var totalHits=document.getElementById("hiddentotalhits").innerHTML;
    var progress_curr = 0;
    var progressinterval = setInterval(function(){
        $.ajax({url: "/updateProgress?sessionID="+sessionID, type: 'GET',success: function(result){
                if (progress_curr == parseInt(result)) {
                    clearInterval(progressinterval);
                    setProgressbar(totalHits, totalHits);

                    activateControl();
                    return;
                }

                progress_curr = parseInt(result);
                setProgressbar(result,totalHits);

            }
        })}, 2000 );




});

