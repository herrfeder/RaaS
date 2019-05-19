/*
$(".alert").delay(4000).slideUp(200, function() {
	$(this).alert('close');
});
*/



$(document).ready (function() {
    $(".alert").alert();
    setTimeout(function() {
        $(".alert").slideUp(500);
        }, 3000);
 })



function flash(message, category) {

    var message = '<div class="alert alert-'+category+'"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>'+message+'</div>';
    $('#messagebox').append(message);
    setTimeout(function() {

        $(".alert").slideUp(500);
        }, 3000);
 };



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


function serveCopy() {

        console.log("serve raw in clipboard");
        /* need to find out how to copy content into clipboard */
  //      document.execCommand('copy');


        //$.ajax({url:"/ServeResults?type=copy&sessionID="+sessionID, type: 'GET', success: function(result){
//
    //}});
};


function serveDownload() {

        console.log("serve download");
        $.ajax({url:"/ServeResults?type=download&sessionID="+sessionID, type: 'GET', success: function(result){
            window.open("/static/results/"+result);
    }});
};






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

