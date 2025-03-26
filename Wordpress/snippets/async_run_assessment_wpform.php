function async_run_assessment_wpforms_markdown_shortcode() {
    ob_start();

    $form_id = 241;
    $user_id = get_current_user_id();
    $entries = wpforms()->entry->get_entries([  // get most recent form entry from user
        'form_id' => $form_id,
        'user_id' => $user_id,
        'number' => 1
        ]);

    if (!empty($entries['entries'])) {
        $latest_entry = $entries['entries'][0];
        $form_data = [
            'name' => $latest_entry['fields'][1]['value'] ?? '',
            'sex' => $latest_entry['fields'][4]['value'] ?? '',
            'age' => $latest_entry['fields'][3]['value'] ?? '',
            'height' => $latest_entry['fields'][7]['value'] ?? '',
            'weight' => $latest_entry['fields'][6]['value'] ?? '',
            'primary_sport' => $latest_entry['fields'][8]['value'] ?? '',
		    'primary_sport_level' => $latest_entry['fields'][37]['value'] ?? '',
			'primary_sport_position' => $latest_entry['fields'][40]['value'] ?? '',
            'secondary_sport' => $latest_entry['fields'][36]['value'] ?? '',
			'secondary_sport_level' => $latest_entry['fields'][39]['value'] ?? '',
			'secondary_sport_position' => $latest_entry['fields'][41]['value'] ?? '',
            'handedness' => $latest_entry['fields'][9]['value'] ?? '',
			'footedness' => $latest_entry['fields'][43]['value'] ?? '',
            'unique_aspect' => $latest_entry['fields'][20]['value'] ?? '',        
            'sprains' => $latest_entry['fields'][26]['value'] ?? '',
            'strains' => $latest_entry['fields'][27]['value'] ?? '',
            'fractures' => $latest_entry['fields'][28]['value'] ?? '',
            'dislocations' => $latest_entry['fields'][29]['value'] ?? '',
            'overuse_&_chronic_injuries' => $latest_entry['fields'][30]['value'] ?? '',
            'head_&_neck_injuries' => $latest_entry['fields'][31]['value'] ?? '',
            'spinal_injuries' => $latest_entry['fields'][32]['value'] ?? ''
            ];
    } else {
        $form_data = ['error' => 'No entries found'];
    }
    ?>
    <!-- Include Marked.js from a CDN -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script>
    document.addEventListener("DOMContentLoaded", function() {
        const formData = <?php echo json_encode($form_data); ?>

        // Global function to poll for the result.
        function pollForResult(task_id) {
            let attempts = 0;
            const maxAttempts = 30;  // Approximately 5 minutes if polling every 10 seconds.
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

                fetch(`https://peakplay.onrender.com/get_result/${task_id}`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        // When the returned result is no longer "Processing..."
                        if (data.result !== "Processing...") {
                            clearInterval(pollingInterval);
                            loadingElem.style.display = "none";
                            
                            // Extract the markdown content from the JSON response.
                            // We assume that data.result is an object with a "result" field containing markdown.
                            let markdown = "";
                            if (typeof data.result === "object" && data.result.result && typeof data.result.result === "string") {
                                markdown = data.result.result;
                            } else if (typeof data.result === "string") {
                                markdown = data.result;
                            } else {
                                markdown = "";
                            }
                            
                            // Use Marked.js to convert the markdown string to HTML.
                            resultElem.innerHTML = marked.parse(markdown);
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
            }, 10000);  // Poll every 10 seconds.
        }

        // Function to initiate the assessment.
        function runFullAssessment() {
            const loadingElem = document.getElementById("loading");
            const resultElem = document.getElementById("result");
            if (loadingElem) {
                loadingElem.style.display = "block";
                loadingElem.innerHTML = "Processing...";
            }
            if (resultElem) {
                resultElem.innerHTML = "";
            }

            fetch("https://peakplay.onrender.com/run_full_assessment", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ form_data: formData } )  
                })
                .then(response => response.json())
                .then(data => pollForResult(data.task_id))
                .catch(error => {
                    loadingElem.style.display = "none";
                    resultElem.innerHTML = "Error occurred.";
                });
            }

            // Attach the runFullAssessment function to the button.
        const btn = document.getElementById("runAssessmentBtn");
        if (btn) {
			btn.style.color = "white";
  		    btn.style.padding = "12px 20px";
			btn.style.fontSize = "16px";
			btn.style.fontWeight = "bold";
			btn.style.border = "none";
			btn.style.borderRadius = "8px";
			btn.style.cursor = "pointer";
			btn.style.width = "250px";
            btn.addEventListener("click", runFullAssessment);
        }
    });
    </script>

    <button id="runAssessmentBtn">Run Full Assessment</button>
    <div id="loading" style="display:none;">Processing...</div>
    <div id="result"></div>
    <?php
    return ob_get_clean();
}
add_shortcode('async_run_assessment_wpforms_shortcode', 'async_run_assessment_wpforms_markdown_shortcode');