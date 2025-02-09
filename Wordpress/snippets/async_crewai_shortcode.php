function async_crewai_shortcode() {
    ob_start();
    ?>
    <script>
    function runAssessment() {
        document.getElementById("loading").style.display = "block";
        document.getElementById("result").innerHTML = "";

        let fileUrl = "https://peakplaysports.com/wp-content/uploads/2025/02/player_profile.txt"; 

        fetch(fileUrl)
        .then(response => response.text())  // ✅ Read file content as text
        .then(fileContent => {
            fetch("https://peakplay.onrender.com/run_assessment", {
                method: "POST",
                headers: {
                    "Content-Type": "text/plain"
                },
                body: fileContent  // ✅ Send file content as plain text
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById("loading").innerHTML = "Processing...";
                pollForResult(data.task_id);  // ✅ Start polling
            })
            .catch(error => {
                document.getElementById("loading").style.display = "none";
                document.getElementById("result").innerHTML = "Error occurred.";
                console.error("Error:", error);
            });
        })
        .catch(error => {
            document.getElementById("loading").style.display = "none";
            document.getElementById("result").innerHTML = "Error fetching file.";
            console.error("Error:", error);
        });
    }

    function pollForResult(taskId) {
        let attempts = 0;
        let maxAttempts = 30;  // ✅ Stop polling after 5 minutes

        function checkResult() {
            fetch(`https://peakplay.onrender.com/get_result/${taskId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.result !== "Processing...") {
                        document.getElementById("loading").style.display = "none";
                        document.getElementById("result").innerHTML = `<pre>${JSON.stringify(data.result, null, 2)}</pre>`;
                    } else if (attempts < maxAttempts) {
                        attempts++;
                        setTimeout(checkResult, 5000);  // ✅ Poll every 5 seconds
                    } else {
                        document.getElementById("loading").style.display = "none";
                        document.getElementById("result").innerHTML = "Timed out. Try again later.";
                    }
                })
                .catch(error => {
                    document.getElementById("loading").style.display = "none";
                    console.error("Error:", error);
                });
        }

        checkResult();
    }
    </script>

    <button onclick="runAssessment()">Run Assessment</button>
    <div id="loading" style="display:none;">Processing...</div>
    <div id="result"></div>
    <?php
    return ob_get_clean();
}
add_shortcode('async_crewai', 'async_crewai_shortcode');