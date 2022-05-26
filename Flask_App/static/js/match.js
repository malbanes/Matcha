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
    node[0].innerHTML = "Croissant";
  }
  else {
    node[0].innerHTML = "Décroissant";
  }
}

// Filtre Gesture //
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
      $('.live-search-list li').each(function(){ 
          if ($(this).filter('[data-search-term *= ' + searchTerm + ']').length > 0 || searchTerm.length < 1) {
              $(this).show();
          } else {
              $(this).hide();
          }
        });
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

//Tri Ajax Gesture
$(function() {
  $('#tri-match-btn').click(function(e) {
      e.preventDefault();
      var form_data = new FormData($('#tri-match-form')[0]);
      $.ajax({
          type: 'POST',
          url: '/trimatch',
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

              } //End else
          },
      });
  });
});

//Filtre Ajax Gesture
$(function() {
  $('#filtre-match-btn').click(function(e) {
      e.preventDefault();
      var form_data = new FormData($('#filtre-match-form')[0]);
      $.ajax({
          type: 'POST',
          url: '/filtrematch',
          data: form_data,
          contentType: false,
          cache: false,
          processData: false,
          success: function(data) {
              if (data == 'KO') {
                  console.log("FILTRE KO");
                  location.reload();
              }
              else {
                  console.log("C'est Filtré !!");
                  location.reload();
              }
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
                if (data == 'KO') {
                  console.log(" TRIER SEARCH KO");
                  //location.reload();
                }
                else {
                  var size = data.all_users.length;
                  for (let index = 0; index < size; ++index) {
                    var element = data.all_users[index];
                    // ...use `element`...
                    var link = document.getElementById('link'+index);
                    if (link != null) {
                      var newlink = "http://127.0.0.1:5000/showprofile/"+element[4];
                      link.href = newlink;
                      var img = document.getElementById('img'+index);
                      img.style.backgroundImage = "url('"+element[3]+"')";
                      var title = document.getElementById('title'+index);
                      title.innerHTML= element[4];
                      var info = document.getElementById('info'+index);
                      info.innerHTML = element[1] + " ans . "+element[2];
                      var like = document.getElementById('like'+index);
                    }
                  }
                }
            },
        });
    });
});
