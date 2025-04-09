//! Core Genkit library for Rust.

// Placeholder function
pub fn hello() -> String {
    "Hello from genkit-rs!".to_string()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        assert_eq!(hello(), "Hello from genkit-rs!");
    }
}
