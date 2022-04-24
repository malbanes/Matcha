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
                  console.log(data);
              }
              else {
                  console.log(data);
              }
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
                  console.log(data);
              }
              else {
                  console.log(data);
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
        e.preventDefault();
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
                    console.log(data);
                }
                else {
                    console.log(data);
                }
            },
        });
    });
});
