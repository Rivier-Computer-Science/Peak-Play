function async_run_full_assessment_markdown_shortcode() {
    ob_start();
    ?>
    <!-- Include Marked.js from a CDN -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script>
    document.addEventListener("DOMContentLoaded", function() {

        // Poll for the assessment result using setInterval.
        function pollForResult(taskId) {
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

                fetch(`https://peakplay.onrender.com/get_result/${taskId}`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        // When the result is no longer "Processing..."
                        if (data.result !== "Processing...") {
                            clearInterval(pollingInterval);
                            loadingElem.style.display = "none";
                            
                            // Extract the markdown string from the JSON response.
                            let markdown = "";
                            if (typeof data.result === "object") {
                                // If the object has a 'markdown' property, use it.
                                if (data.result.markdown && typeof data.result.markdown === "string") {
                                    markdown = data.result.markdown;
                                } else {
                                    // Otherwise, convert the object to a string.
                                    markdown = JSON.stringify(data.result, null, 2);
                                }
                            } else {
                                markdown = data.result;
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

        // Initiate the assessment process.
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

            const fileUrl = "https://peakplaysports.com/wp-content/uploads/2025/02/player_profile.txt"; 

            fetch(fileUrl)
                .then(response => response.text())
                .then(fileContent => {
                    fetch("https://peakplay.onrender.com/run_full_assessment", {
                        method: "POST",
                        headers: {
                            "Content-Type": "text/plain"
                        },
                        body: fileContent
                    })
                    .then(response => response.json())
                    .then(data => {
                        // Once we have the task id, start polling for the result.
                        pollForResult(data.task_id);
                    })
                    .catch(error => {
                        if (loadingElem) {
                            loadingElem.style.display = "none";
                        }
                        if (resultElem) {
                            resultElem.innerHTML = "Error occurred starting the assessment.";
                        }
                        console.error("Error starting assessment:", error);
                    });
                })
                .catch(error => {
                    if (loadingElem) {
                        loadingElem.style.display = "none";
                    }
                    if (resultElem) {
                        resultElem.innerHTML = "Error fetching file.";
                    }
                    console.error("Error fetching file:", error);
                });
        }

        // Attach the runFullAssessment function to the button.
        const btn = document.getElementById("runAssessmentBtn");
        if (btn) {
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
add_shortcode('async_run_full_assessment_markdown', 'async_run_full_assessment_markdown_shortcode');