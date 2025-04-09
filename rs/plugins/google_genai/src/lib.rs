//! Genkit Plugin for Google Generative AI (Gemini).

use genkit;

pub fn plugin_google_genai_hello() -> String {
    let core_msg = genkit::hello();
    format!("Hello from genkit-plugin-google-genai! (using: {})", core_msg)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let result = plugin_google_genai_hello();
        assert!(result.contains("genkit-plugin-google-genai"));
        assert!(result.contains("Hello from genkit-rs!"));
    }
}
