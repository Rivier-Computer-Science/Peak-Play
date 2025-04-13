// AJAX actions for creating pending blog posts
add_action('wp_ajax_create_pending_blog_post', 'create_pending_blog_post_callback');
add_action('wp_ajax_nopriv_create_pending_blog_post', 'create_pending_blog_post_callback');

function create_pending_blog_post_callback() {
    $data = json_decode(file_get_contents('php://input'), true);

    if (empty($data['title']) || empty($data['content'])) {
        wp_send_json_error([
            'message' => 'Title or content missing.',
            'received_data' => $data
        ]);
    }

    $post_title = sanitize_text_field($data['title']);
    $post_content = wp_kses_post($data['content']);

    $user = get_user_by('login', 'PeakPlaySports');
    if (!$user) {
        wp_send_json_error('User PeakPlaySports not found.');
    }

    $new_post = array(
        'post_title'   => $post_title,
        'post_content' => $post_content,
        'post_status'  => 'pending',
        'post_author'  => $user->ID,
        'post_type'    => 'post'
    );

    $post_id = wp_insert_post($new_post);

    if ($post_id && !is_wp_error($post_id)) {
        $category_ids = [];

		// Ensure top-level "Blog" category
		$blog_category = get_category_by_slug('blog');
		if (!$blog_category) {
			$blog_category = wp_insert_term('Blog', 'category');
		}
		$blog_cat_id = is_array($blog_category) ? $blog_category['term_id'] : $blog_category->term_id;
		$category_ids[] = $blog_cat_id;

		// Ensure "Sports" category exists
		$sports_category = get_category_by_slug('sports');
		if (!$sports_category) {
			$sports_category = wp_insert_term('Sports', 'category');
		}
		$sports_cat_id = is_array($sports_category) ? $sports_category['term_id'] : $sports_category->term_id;

		// Assign specific sport under Sports
		if (!empty($data['sport'])) {
			$sport_name = sanitize_text_field($data['sport']);
			$sport_slug = sanitize_title($sport_name);

			$sport_category = get_category_by_slug($sport_slug);
			if (!$sport_category) {
				$sport_category = wp_insert_term($sport_name, 'category', ['parent' => $sports_cat_id]);
			}
			$sport_cat_id = is_array($sport_category) ? $sport_category['term_id'] : $sport_category->term_id;
			$category_ids[] = $sport_cat_id;
		}

		wp_set_post_categories($post_id, $category_ids);

        // Assign post tags
        if (!empty($data['post_tags']) && is_array($data['post_tags'])) {
            $tags = array_map('sanitize_text_field', $data['post_tags']);
            wp_set_post_tags($post_id, $tags, true);
        }

        wp_send_json_success(['post_id' => $post_id]);
    } else {
        wp_send_json_error([
            'message' => 'Failed to create post.',
            'error_details' => $post_id->get_error_message()
        ]);
    }
}






// Shortcode for generating blog post via external API
add_shortcode('async_generate_blog_post_shortcode', 'async_generate_blog_post_shortcode');

function async_generate_blog_post_shortcode() {
    ob_start();
    ?>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script>
    document.addEventListener("DOMContentLoaded", function() {

		function pollForResult(taskId) {
			let attempts = 0;
			const maxAttempts = 30;
			const loadingElem = document.getElementById("loading");
			const resultElem = document.getElementById("result");

			const pollingInterval = setInterval(() => {
				attempts++;
				loadingElem.innerHTML = `Processing... (Attempt ${attempts}/${maxAttempts})`;

				fetch(`https://peakplay.onrender.com/get_result/${taskId}`)
					.then(response => response.json())
					.then(data => {
						console.log("Initial response:", data); // Log the response clearly

						if (data.result === "Processing...") {
							if (attempts >= maxAttempts) {
								clearInterval(pollingInterval);
								loadingElem.style.display = "none";
								resultElem.innerHTML = "Timed out. Try again later.";
							}
							return;
						}

						// String or JSON response accepted
						let parsedInnerJSON;
						try {
							if (typeof data.result === 'string') {
								// Extract JSON from string if needed
								const jsonMatch = data.result.match(/{[\s\S]*}/);
								if (!jsonMatch) throw new Error("No valid JSON found in string result.");

								parsedInnerJSON = JSON.parse(jsonMatch[0]);
							} else if (typeof data.result === 'object') {
								// Already parsed JSON
								parsedInnerJSON = data.result;
							} else {
								throw new Error("Unexpected data.result type: " + typeof data.result);
							}
						} catch (e) {
							clearInterval(pollingInterval);
							loadingElem.style.display = "none";
							resultElem.innerHTML = "Error parsing inner JSON: " + e.message;
							console.error("Parsing error:", e, data.result);
							return;
						}


						if (parsedInnerJSON.result && parsedInnerJSON.result.post_title && parsedInnerJSON.result.post_content) {
							clearInterval(pollingInterval);
							loadingElem.style.display = "none";
							const { post_title, post_content, sport, post_tags } = parsedInnerJSON.result;
							resultElem.innerHTML = marked.parse(post_content);							
							createPendingPost({ post_title, post_content, sport, post_tags });

						} else {
							clearInterval(pollingInterval);
							loadingElem.style.display = "none";
							resultElem.innerHTML = "Parsed JSON structure incorrect.";
							console.error("Unexpected parsed JSON:", parsedInnerJSON);
						}
					})
					.catch(error => {
						clearInterval(pollingInterval);
						loadingElem.style.display = "none";
						resultElem.innerHTML = `Fetch Error: ${error.message}`;
						console.error("Polling fetch error:", error);
					});
			}, 10000);
		}





        function generateBlogPost() {
            const loadingElem = document.getElementById("loading");
            const resultElem = document.getElementById("result");

            loadingElem.style.display = "block";
            loadingElem.innerHTML = "Processing...";
            resultElem.innerHTML = "";

            fetch("https://peakplay.onrender.com/generate_blog_post", {
                method: "POST",
                headers: { "Content-Type": "text/plain" },
                body: " "
            })
            .then(response => response.json())
            .then(data => pollForResult(data.task_id))
            .catch(error => {
                loadingElem.style.display = "none";
                resultElem.innerHTML = "Error starting the blog post generation.";
            });
        }

		function createPendingPost({ post_title, post_content, sport, post_tags }) {
			const htmlContent = marked.parse(post_content);

			fetch("<?php echo admin_url('admin-ajax.php'); ?>?action=create_pending_blog_post", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ 
					title: post_title,
					content: htmlContent,
					sport: sport,
					post_tags: post_tags  // No splitting needed, already an array
				})
			})
			.then(response => response.json())
			.then(data => {
				if (data.success) {
					console.log("Blog post created (pending) with ID:", data.data.post_id);
				} else {
					console.error("Error creating post:", data.data);
					document.getElementById("result").innerHTML += `<div style="color:red;">
						Error creating post: ${JSON.stringify(data.data)}
					</div>`;
				}
			})
			.catch(error => {
				console.error("AJAX fetch error:", error);
				document.getElementById("result").innerHTML += `<div style="color:red;">
					AJAX fetch error: ${error.message}
				</div>`;
			});
		}

        document.getElementById("generateBlogPostBtn").addEventListener("click", generateBlogPost);
    });
    </script>

    <button id="generateBlogPostBtn">Generate Blog Post</button>
    <div id="loading" style="margin-top:10px; display:none;"></div>
    <div id="result" style="margin-top:10px;"></div>

    <?php
    return ob_get_clean();
}