function async_update_program_markdown_shortcode() {
    ob_start();

    $athlete_profile_form_id = 241;
    $user_id = get_current_user_id();
    $athlete_profile_entries = wpforms()->entry->get_entries([  // get most recent form entry from user
        'form_id' => $athlete_profile_form_id,
        'user_id' => $user_id,
        'number' => 1
        ]);
    error_log('Form athlete_profile_entries: ' . print_r($athlete_profile_entries, true));

    $performance_feedback_form_id = 236;
    $performance_feedback_form_entry = wpforms()->entry->get_entries([  // get most recent performance feedback form entry from user
        'form_id' => $performance_feedback_form_id,
        'user_id' => $user_id,
        'number' => 1
        ]);

 
// Grab form fields 
    if (!empty($athlete_profile_entries[0])) {
        $fields = json_decode($athlete_profile_entries[0]->fields, true);
        $update_program_data = [
            'athlete_name' => $fields["1"]['value'] ?? '',
            'sex' => $fields["4"]['value'] ?? '',
            'athlete_age' => $fields["3"]['value'] ?? '',
            'height' => $fields["7"]['value'] ?? '',
            'weight' => $fields["6"]['value'] ?? '',
            'primary_sport' => $fields["8"]['value'] ?? '',
		    'primary_sport_level' => $fields["37"]['value'] ?? '',
			'primary_sport_position' => $fields["40"]['value'] ?? '',
            'secondary_sport' => $fields["36"]['value'] ?? '',

            ];
    } else {
        $update_program_data = ['error' => 'No athlete_profile_entries found'];
    }

    if (!empty($performance_feedback_form_entry[0])) {
        $performance_fields = json_decode($performance_feedback_form_entry[0]->fields, true);
        $update_program_data += [
            'overall_performance' => $performance_fields["3"]['value'] ?? '',
            'difficulty' => $performance_fields["6"]['value'] ?? '',
            'fatigue' => $performance_fields["4"]['value'] ?? '',
            'injuries' => $performance_fields["7"]['value'] ?? '',
            'injury_details' => $performance_fields["8"]['value'] ?? '',
            'motivation_level' => $performance_fields["9"]['value'] ?? '',
            'additional_comments' => $performance_fields["10"]['value'] ?? '',
            ];
    } else {
        $update_program_data += ['error' => 'No performance feedback form entries found'];
    }
    ?>
    <!-- Include Marked.js from a CDN -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script>
    document.addEventListener("DOMContentLoaded", function() {
        const updateProgramData = <?php echo json_encode($update_program_data); ?>;

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
        function updateProgram() {
            const loadingElem = document.getElementById("loading");
            const resultElem = document.getElementById("result");
            if (loadingElem) {
                loadingElem.style.display = "block";
                loadingElem.innerHTML = "Processing...";
            }
            if (resultElem) {
                resultElem.innerHTML = "";
            }

            fetch("https://peakplay.onrender.com/update_program", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ 
                    update_program_data: updateProgramData
                 } )  
                })
                .then(response => response.json())
                .then(data => pollForResult(data.task_id))
                .catch(error => {
                    loadingElem.style.display = "none";
                    resultElem.innerHTML = "Error occurred.";
                });
            }

            // Attach the updateProgram function to the button.
        const btn = document.getElementById("updateProgramBtn");
        if (btn) {
			btn.style.color = "white";
  		    btn.style.padding = "12px 20px";
			btn.style.fontSize = "16px";
			btn.style.fontWeight = "bold";
			btn.style.border = "none";
			btn.style.borderRadius = "8px";
			btn.style.cursor = "pointer";
			btn.style.width = "250px";
            btn.addEventListener("click", updateProgram);
        }
    });
    </script>

    <button id="updateProgramBtn">Update Program</button>
    <div id="loading" style="display:none;">Processing...</div>
    <div id="result"></div>
    <?php
    return ob_get_clean();
}
add_shortcode('async_update_program', 'async_update_program_markdown_shortcode');