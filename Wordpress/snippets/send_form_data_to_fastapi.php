<?php
function async_send_form_data_to_fastapi() {
    ob_start();
    ?>
    <script>
    function runUpdateAssessment() {
        document.getElementById("loading").style.display = "block";
        document.getElementById("result").innerHTML = "";

        let form = document.getElementById("wpforms-236");  // Get WPForms form
        let formData = new FormData(form);  // Extract form data

        fetch("https://peakplay.onrender.com/update_program", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(jsonData)  // Send form data as JSON
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
        let maxAttempts = 60;  // ✅ Stop polling after 10 minutes

        function checkResult() {
            fetch(`https://peakplay.onrender.com/get_result/${taskId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.result !== "Processing...") {
                        document.getElementById("loading").style.display = "none";
                        document.getElementById("result").innerHTML = `<pre>${JSON.stringify(data.result, null, 2)}</pre>`;
                    } else if (attempts < maxAttempts) {
                        attempts++;
                        setTimeout(checkResult, 10000);  // ✅ Poll every 10 seconds
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

    <button onclick="runUpdateProgram()">Run Assessment</button>
    <div id="loading" style="display:none;">Processing...</div>
    <div id="result"></div>
    <?php
    return ob_get_clean();
}
add_shortcode('async_send_form_data_to_fastapi', 'async_update_program_shortcode');
