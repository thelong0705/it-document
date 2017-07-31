$(function () {
    let availableTags;
    $.ajax({
        url: `/categories/all/api`,
        method: "GET",
        data: {},
        success: function (data) {
            availableTags = data.name_list;
            $("#tags").autocomplete({
                source: availableTags
            });
            $("#tags-nav").autocomplete({
                source: availableTags
            });
        }
    });
});

function search() {
    let content;
    if (window.event.keyCode === 13) {
        content = $('#tags').val();
        if (content !== null && content !== ``)
            window.location.href = `/search/${content}`;
    }
}

function searchNav() {
    let content;
    if (window.event.keyCode === 13) {
        content = $('#tags-nav').val();
        if (content !== null && content !== ``)
            window.location.href = `/search/${content}`;
    }
}

function search_by_click() {
    let content;
    content = $('#tags').val();
    if (content !== null && content !== ``)
        window.location.href = `/search/${content}`;
}

function search_by_click_nav() {
    let content;
    content = $('#tags-nav').val();
    if (content !== null && content !== ``)
        window.location.href = `/search/${content}`;
}

