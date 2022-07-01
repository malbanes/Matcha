// Card Gesture
function toggle_display(i){
  var moveOutWidth = document.body.clientWidth;

  el = document.getElementById(i);
     el.className += ' remove-card';
     el.parentNode.removeChild(el);
}
//-------------------//
// Modal Gesture     //
//-------------------//

// Tri Gesture //
function changeIt(i) {
  var node;
  node = i.parentElement.getElementsByTagName("small");
  if (i.checked) {
    node[0].innerHTML = "Increase";
  }
  else {
    node[0].innerHTML = "Decrease";
  }
}

// Filtre Gesture //
function changeLocRangeSearch(loc) {
    document.getElementById("locRangeSearchLabel").innerHTML = loc + " Km";
    document.getElementById("locRangeLabel").innerHTML = loc + " Km";
}

function changeLocRange(loc) {
  document.getElementById("locRangeLabel").innerHTML = loc + " Km";
}




$( function() {
  $( "#slider-range-search" ).slider({
    range: true,
    min: 18,
    max: 99,
    values: [ 18, 99 ],
    slide: function( event, ui ) {
      if (ui.values[ 0 ] == ui.values[ 1 ])
      {
        if (ui.values[ 1 ] == 99) {
          ui.values[ 0 ] = ui.values[ 0 ] - 1;
        }
        else {
          ui.values[ 1 ] = ui.values[ 1 ]  + 1;
        }
      }
      $( "#ageRangeSearch" ).val( ui.values[ 0 ] + " ans" + " et "  + ui.values[ 1 ] + " ans" );
      $("#ageMinSearch").val(ui.values[ 0 ]);
      $("#ageMaxSearch").val(ui.values[ 1 ]);
    }
  });
  $( "#ageRangeSearch" ).val($( "#slider-range-search" ).slider( "values", 0 ) + " ans et " + $( "#slider-range-search" ).slider( "values", 1 ) + " ans");
} );

$( function() {
  $( "#slider-score-range-search" ).slider({
    range: true,
    min: 0,
    max: 9999,
    values: [ 0, 5000 ],
    slide: function( event, ui ) {
      $( "#scoreRangeSearch" ).val( ui.values[ 0 ] + " et " + ui.values[ 1 ]);
      $("#scoreMinSearch").val(ui.values[ 0 ]);
      $("#scoreMaxSearch").val(ui.values[ 1 ]);
    }
  });
  $( "#scoreRangeSearch" ).val($( "#slider-score-range-search" ).slider( "values", 0 ) + " et " + $( "#slider-score-range-search" ).slider( "values", 1 ));
} );

$( function() {
    $( "#slider-range" ).slider({
      range: true,
      min: 18,
      max: 99,
      values: [ 18, 99 ],
      slide: function( event, ui ) {
        if (ui.values[ 0 ] == ui.values[ 1 ])
        {
          if (ui.values[ 1 ] == 99) {
            ui.values[ 0 ] = ui.values[ 0 ] - 1;
          }
          else {
            ui.values[ 1 ] = ui.values[ 1 ]  + 1;
          }
        }
        $( "#ageRange" ).val( ui.values[ 0 ] + " ans" + " et "  + ui.values[ 1 ] + " ans" );
        $("#ageMin").val(ui.values[ 0 ]);
        $("#ageMax").val(ui.values[ 1 ]);
      }
    });
    $( "#ageRange" ).val($( "#slider-range" ).slider( "values", 0 ) + " ans et " + $( "#slider-range" ).slider( "values", 1 ) + " ans");
  } );

  $( function() {
    $( "#slider-score-range" ).slider({
      range: true,
      min: 0,
      max: 9999,
      values: [ 0, 5000 ],
      slide: function( event, ui ) {
        $( "#scoreRange" ).val( ui.values[ 0 ] + " et " + ui.values[ 1 ]);
        $("#scoreMin").val(ui.values[ 0 ]);
        $("#scoreMax").val(ui.values[ 1 ]);
      }
    });
    $( "#scoreRange" ).val($( "#slider-score-range" ).slider( "values", 0 ) + " et " + $( "#slider-score-range" ).slider( "values", 1 ));
  } );

  //Hashtag search
  jQuery(document).ready(function($){
    $('.live-search-list li').each(function(){
      $(this).attr('data-search-term', $(this).text().toLowerCase());
    });
    $('.live-search-box').on('keyup', function(){  
      var searchTerm = $(this).val().toLowerCase();
      searchTerm = searchTerm.replace(/ /g, "");
      //[BUG] sanitize = txt.rstrip(",.qsw") ou Regex "allow a-z car toLowerCase activé" (erreur front console on spécial char)
      if (searchTerm != "") { 
        $('.live-search-list li').each(function(){ 
          //if ($(this).filter('[data-search-term *= ' + searchTerm + ']').length > 0 || searchTerm.length < 1) {
          if (($(this).filter('[data-search-term *= ' + searchTerm + ']').length > 0 || searchTerm.length < 1) || ($(this).filter('[data-tag *= ' + searchTerm+ ']').length > 0 || searchTerm.length < 1) ) {
              $(this).show();
          } else {
              $(this).hide();
          }
        });
      }
    });
  });


  //-----------------------------//
  //   Lazy Load Images          //
  //-----------------------------//

  document.addEventListener("DOMContentLoaded", function() {
    var lazyloadImages;    
  
    if ("IntersectionObserver" in window) {
      lazyloadImages = document.querySelectorAll(".lazy");
      var imageObserver = new IntersectionObserver(function(entries, observer) {
        entries.forEach(function(entry) {
          if (entry.isIntersecting) {
            var image = entry.target;
            image.classList.remove("lazy");
            imageObserver.unobserve(image);
          }
        });
      });
  
      lazyloadImages.forEach(function(image) {
        imageObserver.observe(image);
      });
    } else {  
      console.log("Le else");
      var lazyloadThrottleTimeout;
      lazyloadImages = document.querySelectorAll(".lazy");
      
      function lazyload () {
        if(lazyloadThrottleTimeout) {
          clearTimeout(lazyloadThrottleTimeout);
        }    
  
        lazyloadThrottleTimeout = setTimeout(function() {
          var scrollTop = window.pageYOffset;
          lazyloadImages.forEach(function(img) {
              if(img.offsetTop < (window.innerHeight + scrollTop)) {
                img.src = img.dataset.src;
                console.log(img.src);
                img.classList.remove('lazy');
              }
          });
          if(lazyloadImages.length == 0) { 
            document.removeEventListener("scroll", lazyload);
            window.removeEventListener("resize", lazyload);
            window.removeEventListener("orientationChange", lazyload);
          }
        }, 30);
      }
  
      document.addEventListener("scroll", lazyload);
      window.addEventListener("resize", lazyload);
      window.addEventListener("orientationChange", lazyload);
    }
  })
  

//-----------------------------//
// Match Form ajax Gesture     //
//-----------------------------//

//Card action Gesture
function toggle_display_like(i, outter_loop){
  var moveOutWidth = document.body.clientWidth;
  add_match_like(i);
  console.log(i);
  pass_match(i);
  el = document.getElementById(i);
  if (outter_loop == 3) {
    location = '/match';
  }
  else {
    el.className += ' remove-card';
    el.parentNode.removeChild(el);
  }
}

function toggle_display_pass(i, outter_loop){
  var moveOutWidth = document.body.clientWidth;
  pass_match(i);
  el = document.getElementById(i);
  if (outter_loop == 3) {
    location = '/match';
  }
  else {
    el.className += ' remove-card';
    el.parentNode.removeChild(el);
  }
}

//Pass a match
/*function next_match(user_id) {
  $.ajax({
          type: 'POST',
          url: '/matchnext',
          data: {"data":user_id},
          success: function(data) {
              if (data == "KO") {
                //console.log('Une erreur est survenue');
              }
              else {
                  console.log("Next match");
                  var size = data.final_users.length;
                  for (let index = 0; index < size; ++index) {
                    var element = data.final_users[index];
                    var uid = element[0];
                    // ...use `element`...
                    // create the next card
                    }
              }
          },
      });
  }*/

//Pass a match
function pass_match(user_id) {
  $.ajax({
          type: 'POST',
          url: '/matchpass',
          data: {"data":user_id},
          success: function(data) {
              if (data == "KO") {
                //console.log('Une erreur est survenue');
              }
              else {
                  console.log("Match is passed");
              }
          },
      });
  }


//Add like from match
function add_match_like(user_id) {
  $.ajax({
          type: 'POST',
          url: '/addlike',
          data: {"data":user_id},
          success: function(data) {
              if (data == "KO") {
                //console.log('Une erreur est survenue');
              }
              else {
                  add_notification(user_id , 0, 1);
              }
          },
      });
  }

//Tri Ajax Gesture
$(function() {
  $('#tri-match-btn').click(function(e) {
      //e.preventDefault();
      var form_data = new FormData($('#tri-search-form')[0]);
      $.ajax({
          type: 'POST',
          url: '/trisearch',
          data: form_data,
          contentType: false,
          cache: false,
          processData: false,
          success: function(data) {
              if (data.error == 1) {
                console.log("Tri KO");
              }
              else {
                console.log("c'est trié Match");
                location = '/match';
              } //End else
          },
      });
  });
});

//Tri Ajax Gesture
$(function() {
  $('#filtre-match-btn').click(function(e) {
      //e.preventDefault();
      var form_data = new FormData($('#filtre-search-form')[0]);
      $.ajax({
          type: 'POST',
          url: '/filtresearch',
          data: form_data,
          contentType: false,
          cache: false,
          processData: false,
          success: function(data) {
              if (data == 'KO') {
                console.log("Tri KO");
              }
              else {
                console.log("c'est trié Match");
                location = '/match';
              } //End else
          },
      });
  });
});



//------------------------------//
// search Form ajax Gesture     //
//------------------------------//


  //Tri Ajax Gesture
  $(function() {
    $('#tri-search-btn').click(function(e) {
        //e.preventDefault();
        var form_data = new FormData($('#tri-search-form')[0]);
        $.ajax({
            type: 'POST',
            url: '/trisearch',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            success: function(data) {
                if (data.error == 1) {
                  console.log(" TRIER SEARCH KO");
                  //location.reload();
                }
                else {
                  location = '/search';
                  /*var size = data.all_users.length;
                  for (let index = 0; index < size; ++index) {
                    var element = data.all_users[index];
                    // ...use `element`...
                    var link = document.getElementById('link'+index);
                    if (link != null) {
                      var newlink = "http://127.0.0.1:5000/showprofile/"+element[1];
                      link.href = newlink;
                      var img = document.getElementById('img'+index);
                      img.style.backgroundImage = "url('"+element[4]+"')";
                      var title = document.getElementById('title'+index);
                      title.innerHTML= element[1];
                      var info = document.getElementById('info'+index);
                      info.innerHTML = element[2] + " ans . "+element[3];
                      var like = document.getElementById('like'+index);
                    }
                  }*/
                }
            },
        });
    });
});



//Tri Reset Ajax gesture
$(function() {
  $('#tri-search-reset').click(function(e) {
      e.preventDefault();
      $.ajax({
          type: 'POST',
          url: '/triresetsearch',
          data: 0,
          contentType: false,
          cache: false,
          processData: false,
          success: function(data) {
              if (data == "KO") {
                console.log("RESET Tri SEARCH KO");
              }
              else {
                console.log("RESET Tri search OK")
                /* Reset UI */
                location = '/search';
              }
          },
      });
  });
});

//Filtre Reset Ajax gesture
$(function() {
  $('#filtre-search-reset').click(function(e) {
      e.preventDefault();
      $.ajax({
          type: 'POST',
          url: '/filtreresetsearch',
          data: 0,
          contentType: false,
          cache: false,
          processData: false,
          success: function(data) {
              if (data == "KO") {
                console.log("RESET FILTRE SEARCH KO");
              }
              else {
                console.log("RESET Filtre search OK")
                /* Reset UI */
                location = '/search';
              }
          },
      });
  });
});

//Filtre Ajax Gesture
$(function() {
  $('#filtre-search-btn').click(function(e) {
      e.preventDefault();
      $('#current_page').val(1);
      var form_data = new FormData($('#filtre-search-form')[0]);
      $.ajax({
          type: 'POST',
          url: '/filtresearch',
          data: form_data,
          contentType: false,
          cache: false,
          processData: false,
          success: function(data) {
              if (data.error == 1) {
                console.log("Filtre SEARCH KO");
                //location.reload();
              }
              else {
                console.log("Filtre search OK")
                /* Reset UI */
                location = '/search';
                /*$('#total_user').html(data.user_num + " singles");
                if (data.user_num == 0) {
                  $('#no-user-message').removeClass('d-none');
                }
                else {
                  $('#no-user-message').addClass('d-none');
                }*/
                /* Populate user_list card */
                /*var size = data.all_users.length;
                for (var index = 0; index < size; ++index) {
                  var element = data.all_users[index];
                  // ...use `element`...
                  $('#card'+ index).removeClass('d-none');
                  $('#card'+ index).addClass('d-inline-flex');
                  var link = document.getElementById('link'+index);
                  if (link != null) {
                    var newlink = "http://127.0.0.1:5000/showprofile/"+element[1];
                    link.href = newlink;
                    var img = document.getElementById('img'+index);
                    img.style.backgroundImage = "url('"+element[4]+"')";
                    var title = document.getElementById('title'+index);
                    title.innerHTML= element[1];
                    var info = document.getElementById('info'+index);
                    info.innerHTML = element[2] + " ans . "+element[3];
                    var like = document.getElementById('like'+index);
                  }
                }
                for (var oindex = size; oindex < 20; ++oindex) {
                  $('#card'+ oindex).removeClass('d-inline-flex');
                  $('#card'+ oindex).addClass('d-none');
                }*/
              }
          },
      });
  });
});

function filtredynamique(page) {

  $('#current_page').val(page);
  
  var form_data = new FormData($('#filtre-search-form')[0]);
  $.ajax({
      type: 'POST',
      url: '/filtresearch',
      data: form_data,
      contentType: false,
      cache: false,
      processData: false,
      success: function(data) {
          if (data == 'KO') {
            console.log("Filtre SEARCH KO");
            //location.reload();
          }
          else {
            /* Reset UI */
            $('#total_user').html(data.user_num + " singles");
            if (data.user_num == 0) {
              $('#no-user-message').removeClass('d-none');
            }
            else {
              $('#no-user-message').addClass('d-none');
            }
            /* Populate user_list card */
            var size = data.all_users.length;
            for (var index = 0; index < size; ++index) {
              var element = data.all_users[index];
              // ...use `element`...
              $('#card'+ index).removeClass('d-none');
              $('#card'+ index).addClass('d-inline-flex');
              var link = document.getElementById('link'+index);
              if (link != null) {
                var newlink = "http://127.0.0.1:5000/showprofile/"+element[1];
                link.href = newlink;
                var img = document.getElementById('img'+index);
                img.style.backgroundImage = "url('"+element[4]+"')";
                var title = document.getElementById('title'+index);
                title.innerHTML= element[1];
                var info = document.getElementById('info'+index);
                info.innerHTML = element[2] + " ans . "+element[3];
                var like = document.getElementById('like'+index);
              }
            }
            for (var oindex = size; oindex < 20; ++oindex) {
              $('#card'+ oindex).removeClass('d-inline-flex');
              $('#card'+ oindex).addClass('d-none');
            }
          }
      },
  });

}




