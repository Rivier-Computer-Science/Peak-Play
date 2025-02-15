function async_run_full_assessment_markdown_shortcode() {
    ob_start();
    ?>
    <script>
    document.addEventListener("DOMContentLoaded", function() {
        // Helper function to convert JSON to Markdown.
        function jsonToMarkdown(json) {
            let md = "";
            if (typeof json === "object" && json !== null) {
                for (const key in json) {
                    if (json.hasOwnProperty(key)) {
                        const value = json[key];
                        if (typeof value === "object" && value !== null) {
                            md += `### ${key}\n\n` + jsonToMarkdown(value) + "\n";
                        } else {
                            md += `- **${key}**: ${value}\n`;
                        }
                    }
                }
            } else {
                md = String(json);
            }
            return md;
        }

        // Function to poll for results using setInterval.
        function pollForResult(taskId) {
            let attempts = 0;
            const maxAttempts = 30;  // Approximately 5 minutes if polling every 10 seconds.
            const loadingElem = document.getElementById("loading");
            const resultElem = document.getElementById("result");

            if (!loadingElem || !resultElem) {
                console.error("Missing loading or result element.");
                return;
            }

            // Set up a polling interval.
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
                            const markdown = jsonToMarkdown(data.result);
                            resultElem.innerHTML = `<pre>${markdown}</pre>`;
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

        // Function to initiate the full assessment.
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
                        // Once we have a task id, start polling for the result.
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