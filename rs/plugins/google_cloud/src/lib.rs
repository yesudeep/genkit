//! Genkit Plugin for Google Cloud integrations.

use genkit;

pub fn plugin_google_cloud_hello() -> String {
    let core_msg = genkit::hello();
    format!("Hello from genkit-plugin-google-cloud! (using: {})", core_msg)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let result = plugin_google_cloud_hello();
        assert!(result.contains("genkit-plugin-google-cloud"));
        assert!(result.contains("Hello from genkit-rs!"));
    }
}
