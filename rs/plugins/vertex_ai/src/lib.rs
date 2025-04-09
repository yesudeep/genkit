//! Genkit Plugin for Google Cloud Vertex AI.

use genkit;

pub fn plugin_vertex_ai_hello() -> String {
    let core_msg = genkit::hello();
    format!("Hello from genkit-plugin-vertex-ai! (using: {})", core_msg)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let result = plugin_vertex_ai_hello();
        assert!(result.contains("genkit-plugin-vertex-ai"));
        assert!(result.contains("Hello from genkit-rs!"));
    }
}
