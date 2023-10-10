let disabled = false; // when working, it is disabled

window.onload = function() {
    setObs();
    
    let img = document.getElementById("camera");
    img.onclick = function(event) {
        if (disabled) return;
        let len = img.clientHeight;
        let y = Math.floor((event.x - img.x) / len * img_size);
        let x = Math.floor((event.y - img.y) / len * img_size);
        console.log(x, y)
        object = whichObject(x, y);
        if (object) {
            if (object.type <= 1) {
                if (confirm("Are you sure to choose " + object.name + "?")) {
                    act("get_object", {"object": object.id})
                }
            } else {
                alert("Cannot get object " + object.name + ".");
            }
        }
    }
}

function ajaxPost(url, data, fnSucceed, fnFail, fnLoading=undefined) {
    var ajax = new XMLHttpRequest();
    ajax.open("post", url, true);
    ajax.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    ajax.onreadystatechange = function() {
        if (ajax.readyState == 4) {
            if (ajax.status == 200) fnSucceed(ajax.responseText);
            else fnFail(ajax.statusText);
        } else if (fnLoading) fnLoading();
    }
    ajax.send(JSON.stringify(data));
}

/**
 * Send a action with parameters to server.
 * @param {string} action 
 * @param {*} param 
 */
function act(action, param = {}) {
    // Set button disabled to prevent clicking too fast.
    let buttons = document.getElementsByTagName("button");
    for (let i = 0; i < buttons.length; i++)
        buttons[i].disabled = true;
    disabled = true;
    enableButtons = () => {
        for (let i = 0; i < buttons.length; i++)
            buttons[i].disabled = false;
        disabled = false;
    }
    
    ajaxPost("/action/" + action, param, text => { 
        let img = document.getElementById("camera");
        img.src = "/first_person_img?t=" + new Date().getTime();
        enableButtons();
        obs = JSON.parse(text)
        setObs()
    }, text => {
        alert("Failed: " + text);
        enableButtons();
    });
}

/**
 * Set some HTML elements by observations.
 */
function setObs() {
    document.getElementById("left_hand_object").innerText = JSON.stringify(obs["held_objects"][0])
    document.getElementById("right_hand_object").innerText = JSON.stringify(obs["held_objects"][1])
    document.getElementById("oppo_left_hand_object").innerText = JSON.stringify(obs["oppo_held_objects"][0])
    document.getElementById("oppo_right_hand_object").innerText = JSON.stringify(obs["oppo_held_objects"][1])
    document.getElementById("self_message").innerText = JSON.stringify(obs["messages"][0])
    document.getElementById("oppo_message").innerText = JSON.stringify(obs["messages"][1])
}

/**
 * Get a getable object near pixel (x, y). Pick the one with maximum number of appearances near (x, y).
 * @param {int} x 
 * @param {int} y 
 */
function whichObject(x, y) {
    let rlen = Math.floor(img_size / 128); // range length to search
    let max_app_getable = 0, getable = null, max_app_all = 0, all = null;
    obs["visible_objects"].forEach(object => {
        seg_color = object.seg_color.toString();
        let napp = 0; //number of appearances
        for (let i = Math.max(x - rlen, 0); i <= Math.min(x + rlen, img_size - 1); i++) {
            for (let j = Math.max(y - rlen, 0); j <= Math.min(y + rlen, img_size - 1); j++) {
                if (seg_color == obs.seg_mask[i][j].toString())
                    napp += 1;
            }
        }
        object.napp = napp;
        if (max_app_all < napp) {
            max_app_all = napp;
            all = object;
        }
        if (object.type <= 1 && max_app_getable < napp) {
            max_app_getable = napp;
            getable = object;
        }
    });
    if (max_app_getable == 0) { //No getable object.
        return all;
    }
    return getable;
}