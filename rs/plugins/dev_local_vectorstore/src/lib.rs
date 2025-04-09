//! Genkit Plugin for Development Local Vector Store.

use genkit;

pub fn plugin_dev_local_vectorstore_hello() -> String {
    let core_msg = genkit::hello();
    format!("Hello from genkit-plugin-dev-local-vectorstore! (using: {})", core_msg)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let result = plugin_dev_local_vectorstore_hello();
        assert!(result.contains("genkit-plugin-dev-local-vectorstore"));
        assert!(result.contains("Hello from genkit-rs!"));
    }
}
