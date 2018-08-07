function update_token(url) {
        if(!confirm("Do you really want to generate a new authentication token? " +
                "You current token becomes invalid with this operation.")){
        return;
    }
    var xhttp = new XMLHttpRequest();
    var csrftoken = getCookie('csrftoken');
    console.log(csrftoken);
    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {
            if(this.status === 200){
                window.location.reload(true);
            }
            else{
                alert("Received response with status code: "+String(this.status));
                alert(this.responseText);
            }
        }
    };
    xhttp.open("POST", url, true);
    xhttp.setRequestHeader("X-CSRFToken",csrftoken);
    xhttp.send();
}

function get_token(url) {
var xhttp = new XMLHttpRequest();
    var csrftoken = getCookie('csrftoken');
    console.log(csrftoken);
    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {
            if(this.status === 200){
                document.getElementById("token").innerHTML = String(JSON.parse(xhttp.responseText).token);
            }
            else{
                alert("Received response with status code: "+String(this.status));
                alert(this.responseText);
                return null;
            }
        }
    };
    xhttp.open("GET", url, true);
    xhttp.setRequestHeader("X-CSRFToken",csrftoken);
    xhttp.send();
}