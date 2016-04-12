ckan.module('statsresources-js-autosubmit', function($, _){
    "use strict";
    return {
        initialize: function(){
            $(".js-auto-submit").on('change', function (event) {
              $(event.target).closest("form").submit();
          });
        }
    }
});
