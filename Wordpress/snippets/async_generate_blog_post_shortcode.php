// AJAX handler to create a pending blog post.
add_action('wp_ajax_create_pending_blog_post', 'create_pending_blog_post_callback');
add_action('wp_ajax_nopriv_create_pending_blog_post', 'create_pending_blog_post_callback');

function create_pending_blog_post_callback() {
    $data = json_decode(file_get_contents('php://input'), true);
    if (empty($data['content'])) {
        wp_send_json_error('No content provided.');
    }
    $post_content = wp_kses_post($data['content']);
    
    // Look up the user by username "PeakPlaySports".
    $user = get_user_by('login', 'PeakPlaySports');
    if (!$user) {
        wp_send_json_error('User PeakPlaySports not found.');
    }
    
    // Create a new pending post.
    $new_post = array(
        'post_title'   => 'Auto-generated Post - ' . date("Y-m-d H:i:s"),
        'post_content' => $post_content,
        'post_status'  => 'pending',
        'post_author'  => $user->ID,
        'post_type'    => 'post'
    );
    $post_id = wp_insert_post($new_post);
    if ($post_id && !is_wp_error($post_id)) {
        wp_send_json_success(array('post_id' => $post_id));
    } else {
        wp_send_json_error('Failed to create post.');
    }
}

// Shortcode to generate a blog post.
function async_generate_blog_post_shortcode() {
    ob_start();
    ?>
    <!-- Include Marked.js from CDN -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script>
    document.addEventListener("DOMContentLoaded", function() {

        // Poll for the result from the external API.
        function pollForResult(taskId) {
            let attempts = 0;
            const maxAttempts = 10; // Approximately 5 minutes (polling every 10 seconds).
            const loadingElem = document.getElementById("loading");
            const resultElem = document.getElementById("result");

            if (!loadingElem || !resultElem) {
                console.error("Missing loading or result element.");
                return;
            }

            const pollingInterval = setInterval(() => {
                attempts++;
                const remaining = maxAttempts - attempts;
                loadingElem.innerHTML = `Processing... (Attempt ${attempts} of ${maxAttempts}, ${remaining} remaining)`;
                console.log(`Polling: Attempt ${attempts} of ${maxAttempts}, ${remaining} remaining`);

                fetch(`https://peakplay.onrender.com/get_result/${taskId}`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (data.result !== "Processing...") {
                            clearInterval(pollingInterval);
                            loadingElem.style.display = "none";
                            
                            // Extract markdown from the response.
                            let markdown = "";
                            if (typeof data.result === "object" && data.result.result && typeof data.result.result === "string") {
                                markdown = data.result.result;
                            } else if (typeof data.result === "string") {
                                markdown = data.result;
                            }
                            
                            // Render the markdown using Marked.js.
                            resultElem.innerHTML = marked.parse(markdown);
                            
                            // Send the markdown to create a pending blog post.
                            createPendingPost(markdown);
                        } else if (attempts >= maxAttempts) {
                            clearInterval(pollingInterval);
                            loadingElem.style.display = "none";
                            resultElem.innerHTML = "Timed out. Try again later.";
                        }
                    })
                    .catch(error => {
                        clearInterval(pollingInterval);
                        loadingElem.style.display = "none";
                        resultElem.innerHTML = `Error fetching result: ${error.message}`;
                        console.error("Error fetching result:", error);
                    });
            }, 10000);
        }

        // Function to initiate generating the blog post.
        function generateBlogPost() {
            const loadingElem = document.getElementById("loading");
            const resultElem = document.getElementById("result");
            if (loadingElem) {
                loadingElem.style.display = "block";
                loadingElem.innerHTML = "Processing...";
            }
            if (resultElem) {
                resultElem.innerHTML = "";
            }

            // Call the external endpoint.
            fetch("https://peakplay.onrender.com/generate_blog_post", {
                method: "POST",
                headers: {
                    "Content-Type": "text/plain"
                },
                body: " "  //Empty
            })
            .then(response => response.json())
            .then(data => {
                // Once we have the task ID, start polling for the markdown result.
                pollForResult(data.task_id);
            })
            .catch(error => {
                if (loadingElem) {
                    loadingElem.style.display = "none";
                }
                if (resultElem) {
                    resultElem.innerHTML = "Error occurred starting the blog post generation.";
                }
                console.error("Error starting blog post generation:", error);
            });
        }

        // Function to create a pending blog post via AJAX.
        function createPendingPost(content) {
            fetch("<?php echo admin_url('admin-ajax.php'); ?>?action=create_pending_blog_post", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ content: content })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log("Blog post created (pending approval) with ID: " + data.data.post_id);
                } else {
                    console.error("Error creating blog post: " + data.data);
                }
            })
            .catch(error => console.error("Error creating blog post:", error));
        }

        // Attach the generateBlogPost function to the button.
        const btn = document.getElementById("generateBlogPostBtn");
        if (btn) {
            btn.addEventListener("click", generateBlogPost);
        }
    });
    </script>

    <button id="generateBlogPostBtn">Generate Blog Post</button>
    <div id="loading" style="margin-top:10px;"></div>
    <div id="result" style="margin-top:10px;"></div>
    <?php
    return ob_get_clean();
}
add_shortcode('async_generate_blog_post_shortcode', 'async_generate_blog_post_shortcode');
