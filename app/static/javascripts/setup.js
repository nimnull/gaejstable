exports = this.exports || this;

(function($) {
  exports.Setup = function (options) {
    this.options = options;

    $(".setup .category a").click(function(evt) {
      $.post(evt.currentTarget.href, function(resp){
        var $linkParent = $(evt.currentTarget).parent();
        if (resp.status == 'success') {
          if (resp.data == 'created') $linkParent.addClass("active");
          else if (resp.data == 'deleted') $linkParent.removeClass("active");
        } else {
          console.log(resp);
        };
      });
      return false;
    });
  }
})(jQuery);
