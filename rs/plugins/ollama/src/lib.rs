//! Genkit Plugin for Ollama.

use genkit;

pub fn plugin_ollama_hello() -> String {
    let core_msg = genkit::hello();
    format!("Hello from genkit-plugin-ollama! (using: {})", core_msg)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let result = plugin_ollama_hello();
        assert!(result.contains("genkit-plugin-ollama"));
        assert!(result.contains("Hello from genkit-rs!"));
    }
}
