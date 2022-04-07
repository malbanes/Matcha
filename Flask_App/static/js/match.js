function toggle_display(i){
    var moveOutWidth = document.body.clientWidth;
  
    el = document.getElementById(i);
       el.className += ' remove-card';
       el.parentNode.removeChild(el);
  
  
  }
  
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
  
  function changeLocRange(loc) {
    document.getElementById("locRangeLabel").innerHTML = loc + " Km";
  }
  
  $( function() {
      $( "#slider-range" ).slider({
        range: true,
        min: 18,
        max: 99,
        values: [ 18, 99 ],
        slide: function( event, ui ) {
          $( "#ageRange" ).val( ui.values[ 0 ] + " ans" + " et "  + ui.values[ 1 ] + " ans" );
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
        }
      });
      $( "#scoreRange" ).val($( "#slider-score-range" ).slider( "values", 0 ) + " et " + $( "#slider-score-range" ).slider( "values", 1 ));
    } );