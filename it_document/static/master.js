$("#add-cat-btn").click(function (e) {
    console.log("new");
    e.preventDefault();
    var this_ = $(this);
    var name = $("#add-cat-input").val();
    var api_url = 'http://127.0.0.1:8000/categories/api/add_category/'+name;
    var count = $('#category-choice').length;
    console.log("new");
    $.ajax({
        url: api_url,
        method: "GET",
        data: {},
        success: function (data) {
            if (data.created) {
                var o = new Option(name, data.pk);
                $(o).html(name);
                $("#category-choice").append(o);
                $("#add-cat-input").val("");
            }
        },
        error: function (error) {
        }
    })
});
