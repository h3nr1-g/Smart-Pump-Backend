function delete_and_reload(url) {
    if(!confirm("Do you really want to delete this item?")){
        return;
    }
    var xhttp = new XMLHttpRequest();
    var csrftoken = getCookie('csrftoken');
    console.log(csrftoken);
    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {
            if(this.status === 200){
                window.location.reload(true);
                return;
            }
            if(this.status === 403){
                alert("You do not have permission to perform this action.");
            }
            else{
                alert("Received response with status code: "+String(this.status));
                alert(this.responseText);
            }
        }
    };
    xhttp.open("DELETE", url, true);
    xhttp.setRequestHeader("X-CSRFToken",csrftoken);
    xhttp.send();
}