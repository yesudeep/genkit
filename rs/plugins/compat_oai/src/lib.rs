//! Genkit Plugin for OpenAI Compatibility Layer.

use genkit;

pub fn plugin_compat_oai_hello() -> String {
    let core_msg = genkit::hello();
    format!("Hello from genkit-plugin-compat-oai! (using: {})", core_msg)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let result = plugin_compat_oai_hello();
        assert!(result.contains("genkit-plugin-compat-oai"));
        assert!(result.contains("Hello from genkit-rs!"));
    }
}
