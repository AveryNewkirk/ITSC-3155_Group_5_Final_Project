/*
Infinite scroll functon
Detectes when the user goes to the bottom of page trigger a get request for more posts
*/


function loadMorePosts() {
    $.get('/get_data', function(data) {

        if (data == 'STOP'){
            return;
        }
        console.log('data received ',data)
        $('#post-container').append(data.html);
    });
}

loadMorePosts();

$(window).scroll(function() {
    if ($(window).scrollTop() + $(window).height() >= $(document).height() - 100) {
        loadMorePosts();
    }
});