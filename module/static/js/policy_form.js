$(function() {
      $("#and_or_selecttest").on("change", function(event){
        $.ajax({
          data: {
            test : $(regex).val()
          },
          type:"POST",
          url : "/policy"
        })
        .done(function(data){
        });
      });
});