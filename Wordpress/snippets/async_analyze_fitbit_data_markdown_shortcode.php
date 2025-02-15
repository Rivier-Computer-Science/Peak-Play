function async_analyze_fitbit_data_markdown_shortcode() {
    ob_start();
    ?>
    <!-- Include Marked.js from a CDN -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script>
    document.addEventListener("DOMContentLoaded", function() {

        // Global function to poll for the result.
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
        function analyzeFitbitData() {
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
                    fetch("https://peakplay.onrender.com/analyze_fitbit_data", {
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
                            resultElem.innerHTML = "Error occurred starting the fitbit analysis.";
                        }
                        console.error("Error starting fitbit analysis:", error);
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
        const btn = document.getElementById("analyzeFitbitDataBtn");
        if (btn) {
            btn.addEventListener("click", analyszeFitbitData);
        }
    });
    </script>

    <button id="analyzeFitbitDataBtn">Analyze Fitbit Data</button>
    <div id="loading" style="display:none;">Processing...</div>
    <div id="result"></div>
    <?php
    return ob_get_clean();
}
add_shortcode('async_analyze_fitbit_markdown', 'async_analyze_fitbit_markdown_shortcode');