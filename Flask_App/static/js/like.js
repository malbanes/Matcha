
//Like Gesture
function like_gesture(user_id) {
    var like_id = "like_img"+user_id;
    var like_img = document.getElementById(like_id);
    var is_liked = like_img.classList.contains("red-color");
    if (is_liked == true) {
        delete_like(user_id);
    }
    else {
        add_like(user_id);
    }
}

function add_like(user_id) {
$.ajax({
        type: 'POST',
        url: '/addlike',
        data: {"data":user_id, "csrf_token":crsfToken},
        success: function(data) {
            if (data == "KO") {
              data="KO";
            }
            else {
                var like_id = "like_img"+user_id;
                var like_img = document.getElementById(like_id);
                like_img.classList.add("red-color");
                var message_id = "like_message"+user_id;
                var like_message = document.getElementById(message_id);
                if (like_message) {
                    like_message.style.display = "none";
                }
                add_notification(user_id , 0, 1);
                //If match : send match notif
                if (data == "match") {
                    add_notification(user_id , 2, 2);
                }
            }
        },
    });
}

function delete_like(user_id) {
$.ajax({
        type: 'POST',
        url: '/dellike',
        data: {"data":user_id, "csrf_token":crsfToken},
        success: function(data) {
            if (data == 'KO') {
              //console.log('Une erreur est survenue');
            }
            else {
                var like_id = "like_img"+user_id;
                var like_img = document.getElementById(like_id);
                like_img.classList.remove("red-color");
                var message_id = "like_message"+user_id;
                var like_message = document.getElementById(message_id);
                if (like_message) {
                    like_message.style.display = "none";
                }
                if (data != "Old") {
                    var socket = io();
                    if (data == "Match") {
                        socket.emit('new_notif', {'content': "1", 'receiver' : user_id, 'notif_type': 3});
                    }
                    else {
                        socket.emit('new_notif', {'content': "-1", 'receiver' : user_id, 'notif_type': 0});
                    }
                }
            }
        },
    });
}

//Report Gesture
function report(user_id) {
$.ajax({
        type: 'POST',
        url: '/report',
        data: {"data":user_id, "csrf_token":crsfToken},
        success: function(data) {
          location.reload();
        },
    });
}

//Report Gesture
function block(user_id) {
$.ajax({
        type: 'POST',
        url: '/block',
        data: {"data":user_id, "csrf_token":crsfToken},
        success: function(data) {
            if (data == 'KO') {
              //console.log('Une erreur est survenue');
            }
            else {
              var blockelem = document.getElementById('blockbtn');
              blockelem.classList.add('d-none');
              var unblockelem = document.getElementById('unblockbtn');
              unblockelem.classList.remove('d-none');
              location.reload();
              }
        },
    });
}

function unblock(user_id) {
$.ajax({
        type: 'POST',
        url: '/unblock',
        data: {"data":user_id, "csrf_token":crsfToken},
        success: function(data) {
            if (data == 'KO') {
              //console.log('Une erreur est survenue');
            }
            else {
              var unblockelem = document.getElementById('unblockbtn');
              unblockelem.classList.add('d-none');
              var blockelem = document.getElementById('blockbtn');
              blockelem.classList.remove('d-none');
              location.reload();
            }
        },
    });
}