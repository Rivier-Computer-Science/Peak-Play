add_shortcode('custom_blog_page', 'custom_blog_page_shortcode');

function custom_blog_page_shortcode() {
    ob_start();

    $allowed_authors = ['PeakPlaySports']; // Change author usernames if needed
    $author_ids = array_map(function($login) {
        $user = get_user_by('login', $login);
        return $user ? $user->ID : 0;
    }, $allowed_authors);

    $blog_query = new WP_Query([
        'author__in' => $author_ids,
        'post_status' => 'publish',
        'posts_per_page' => 10,
        'paged' => get_query_var('paged') ? get_query_var('paged') : 1
    ]);

    if ($blog_query->have_posts()):
        while ($blog_query->have_posts()): $blog_query->the_post(); ?>
            <article>
                <h2><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>
                <div><?php the_excerpt(); ?></div>
            </article>
        <?php endwhile;

        echo paginate_links(['total' => $blog_query->max_num_pages]);

    else: ?>
        <p>No posts available.</p>
    <?php endif;

    wp_reset_postdata();

    return ob_get_clean();
}