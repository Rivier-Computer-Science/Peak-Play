// AJAX actions for creating pending blog posts
add_action('wp_ajax_create_pending_blog_post', 'create_pending_blog_post_callback');
add_action('wp_ajax_nopriv_create_pending_blog_post', 'create_pending_blog_post_callback');

function create_pending_blog_post_callback() {
    $data = json_decode(file_get_contents('php://input'), true);

    if (empty($data['content'])) {
        wp_send_json_error('No content provided.');
    }

    // First decode the outer JSON
    $outer_json = json_decode($data['content'], true);
    if (!$outer_json || empty($outer_json['result'])) {
        wp_send_json_error([
            'message' => 'Invalid JSON format (outer level).',
            'received_data' => $data['content']
        ]);
    }

    // Then decode the inner wrapped JSON string
    $inner_json = json_decode($outer_json['result'], true);
    if (!$inner_json || empty($inner_json['result']['post_title']) || empty($inner_json['result']['post_content'])) {
        wp_send_json_error([
            'message' => 'Invalid JSON format (inner level).',
            'received_inner_json' => $outer_json['result']
        ]);
    }

    $post_title = sanitize_text_field($inner_json['result']['post_title']);
    $post_content = wp_kses_post($inner_json['result']['post_content']);

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
        wp_send_json_success(['post_id' => $post_id]);
    } else {
        wp_send_json_error('Failed to create post.');
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
			const maxAttempts = 10;
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

						let parsedInnerJSON;

						try {
							// Fix potential trailing characters by extracting valid JSON only
							const jsonMatch = data.result.match(/{[\s\S]*}/);
							if (!jsonMatch) throw new Error("No valid JSON found in result.");

							parsedInnerJSON = JSON.parse(jsonMatch[0]);
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

							const { post_title, post_content } = parsedInnerJSON.result;

							resultElem.innerHTML = marked.parse(post_content);

							createPendingPost({ post_title, post_content });
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

		function createPendingPost({post_title, post_content}) {
			fetch("<?php echo admin_url('admin-ajax.php'); ?>?action=create_pending_blog_post", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ 
					content: JSON.stringify({
						success: true,
						result: JSON.stringify({
							success: true,
							result: {
								post_title,
								post_content
							}
						})
					})
				})
			})
			.then(response => response.json())
			.then(data => {
				if (data.success) {
					console.log("Blog post created (pending) with ID:", data.data.post_id);
				} else {
					console.error("Error creating post:", data.data);
					// Display detailed error message directly on your webpage for easy debugging:
					document.getElementById("result").innerHTML += `<div style="color:red; margin-top:10px;">
						Error creating post: ${JSON.stringify(data.data)}
					</div>`;
				}
			})
			.catch(error => {
				console.error("AJAX fetch error:", error);
				document.getElementById("result").innerHTML += `<div style="color:red; margin-top:10px;">
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