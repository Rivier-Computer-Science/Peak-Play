function async_log_training() {
    ob_start();
    ?>
    <script>
    function logTraining() {
        document.getElementById("loading").style.display = "block";
        document.getElementById("result").innerHTML = "";

        let form = document.getElementById("wpforms-2032");
        let formData = new FormData(form);  

        // Convert FormData to JSON
        let jsonData = {};
        formData.forEach((value, key) => { jsonData[key] = value; });

        // File URL
        let fileUrl = "https://peakplaysports.com/wp-content/uploads/2025/02/player_profile.txt";

        // Fetch the file and add its contents to the request
        fetch(fileUrl)
        .then(response => response.text())
        .then(fileContent => {
            jsonData["file_content"] = fileContent; // Include file content in the API request

            return fetch("https://peakplay.onrender.com/log_training", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(jsonData)  
            });
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById("loading").innerHTML = "Processing...";
            pollForResult(data.task_id);
        })
        .catch(error => {
            document.getElementById("loading").style.display = "none";
            document.getElementById("result").innerHTML = "Error occurred.";
            console.error("Error:", error);
        });
    }

    function pollForResult(taskId) {
        let attempts = 0;
        let maxAttempts = 60;  

        function checkResult() {
            fetch(`https://peakplay.onrender.com/get_result/${taskId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.result !== "Processing...") {
                        document.getElementById("loading").style.display = "none";

                        // Open a new page with the response
                        let newPage = window.open("", "_blank");
                        newPage.document.write("<html><head><title>Result</title></head><body>");
                        newPage.document.write("<h2>API Response:</h2>");
                        newPage.document.write("<pre>" + JSON.stringify(data.result, null, 2) + "</pre>");
                        newPage.document.write("</body></html>");
                        newPage.document.close();

                    } else if (attempts < maxAttempts) {
                        attempts++;
                        setTimeout(checkResult, 10000);  
                    } else {
                        document.getElementById("loading").style.display = "none";
                        document.getElementById("result").innerHTML = "Timed out. Try again later.";
                    }
                })
                .catch(error => {
                    document.getElementById("loading").style.display = "none";
                    document.getElementById("result").innerHTML = "Error fetching result.";
                    console.error("Error:", error);
                });
        }

        checkResult();
    }
    </script>

    <button onclick="logTraining()">Log Training</button>
    <div id="loading" style="display:none;">Processing...</div>
    <div id="result"></div>
    <?php
    return ob_get_clean();
}
add_shortcode('async_log_training', 'async_log_training');