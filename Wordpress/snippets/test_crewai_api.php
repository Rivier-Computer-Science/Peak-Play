function test_crewai_api() {
    $api_url = "https://peakplay.onrender.com";
    $response = wp_remote_get($api_url);

    if (is_wp_error($response)) {
        return "API Error: " . $response->get_error_message();
    } else {
        return "API is reachable. Status: " . wp_remote_retrieve_response_code($response);
    }
}
add_shortcode('test_crewai', 'test_crewai_api');