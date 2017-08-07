$(function () {
    let availableTags;
    $.ajax({
        url: `/categories/all/api`,
        method: "GET",
        data: {},
        success: function (data) {
            availableTags = data.obj_list;
            if ($('#tags').length) {
                $("#tags").autocomplete({
                    source: availableTags,
                    select: function (event, ui) {
                        window.location = ui.item.url;
                    }
                }).autocomplete(`instance`)._renderItem = function (ul, item) {
                    return $(`<li>`)
                        .append(`<div>${item.value} ${item.des}</div>`)
                        .appendTo(ul);
                };
            }
            if ($('#tags-nav').length) {
                $("#tags-nav").autocomplete({
                    source: availableTags,
                    select: function (event, ui) {
                        window.location = ui.item.url;
                    }
                }).autocomplete(`instance`)._renderItem = function (ul, item) {
                    return $(`<li>`)
                        .append(`<div>${item.value} ${item.des}</div>`)
                        .appendTo(ul);
                };
            }
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

$(document).ready(function () {
    $(`.loader`).hide();
    $(`.star-loader`).hide();
    $(`.loader-comment`).hide();
});
