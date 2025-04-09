use genkit;

fn main() {
    println!("Running ollama_hello sample...");
    // Placeholder - Add logic using genkit and potentially ollama plugin
    let core_msg = genkit::hello();
    println!("Core genkit message: {}", core_msg);
    println!("ollama_hello finished.");
}
