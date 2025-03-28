import streamlit as st
import google.generativeai as genai
import os
from datetime import datetime
import yaml

# Set page configuration
st.set_page_config(
    page_title="Cloud Infrastructure Code Generator",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to initialize the Gemini API using the environment variable
def initialize_gemini_api():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-pro')

# Function to generate code based on user input
def generate_code(model, tool_type, requirements):
    prompts = {
        "ansible": f"""Generate a complete Ansible playbook based on the following requirements:
        
Requirements:
{requirements}

Please provide a well-structured, production-ready Ansible playbook with detailed comments.
Include proper error handling, idempotent tasks, and follow best practices.
""",
        "docker": f"""Generate a production-ready Dockerfile based on the following requirements:
        
Requirements:
{requirements}

Please include:
1. Proper base image selection
2. All necessary installation steps
3. Best practices for Docker (multi-stage builds if appropriate, minimizing layers, etc.)
4. Proper environment setup
5. Detailed comments explaining each step
""",
        "terraform": f"""Generate Terraform code (HCL) for the following infrastructure requirements:
        
Requirements:
{requirements}

The code should:
1. Follow Terraform best practices
2. Include proper variable declarations
3. Use modules where appropriate
4. Include detailed comments
5. Handle dependencies properly
"""
    }
    response = model.generate_content(prompts[tool_type])
    return response.text

# Main application interface
def main():
    st.title("☁️ Cloud Infrastructure Code Generator")
    st.markdown("""
    Generate production-ready infrastructure as code using Google's Gemini AI model.
    """)

    # Sidebar configuration (using environment variable for API key)
    with st.sidebar:
        st.header("Configuration")
        st.info("Using API key from environment variable: GEMINI_API_KEY")
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This application uses Google's Gemini 1.5 Pro model to generate:
        - Ansible Playbooks
        - Dockerfiles
        - Terraform Configurations
        """)

    # Initialize session state for generated code
    if 'generated_code' not in st.session_state:
        st.session_state.generated_code = ""

    # Main content area: select tool type
    tool_type = st.radio(
        "Select the type of code to generate:",
        ["ansible", "docker", "terraform"],
        index=0,
        help="Choose the code generation tool that fits your needs."
    )

    # Tool-specific inputs
    st.subheader(f"Generate {tool_type.capitalize()} Code")

    # Common requirements text area
    requirements = st.text_area(
        "Describe your requirements in detail:",
        height=200,
        placeholder="E.g., For Ansible: Set up a web server with Nginx and deploy a Node.js application...\n"
                    "For Docker: Create a container for a Python Flask application with Redis...\n"
                    "For Terraform: Create an AWS infrastructure with a VPC, 2 EC2 instances, and an RDS database..."
    )

    # Generate button
    if st.button("Generate Code", type="primary"):
        if not requirements:
            st.warning("Please enter your requirements.")
        else:
            try:
                with st.spinner("Generating code... This may take a moment."):
                    # Initialize the Gemini model using the environment variable
                    model = initialize_gemini_api()
                    # Generate code based on user input
                    st.session_state.generated_code = generate_code(model, tool_type, requirements)
                st.success("Code generated successfully!")
            except Exception as e:
                st.error(f"Error generating code: {str(e)}")

    # Display generated code if available
    if st.session_state.generated_code:
        st.subheader("Generated Code")

        # Determine file extension based on tool type
        extensions = {
            "ansible": "yml",
            "docker": "Dockerfile",
            "terraform": "tf"
        }
        file_extension = extensions[tool_type]
        file_name = f"{tool_type}_generated.{file_extension}"

        # Render the markdown content as received from the API.
        st.markdown(st.session_state.generated_code, unsafe_allow_html=True)

        # Download button for the generated code
        st.download_button(
            label="Download Code",
            data=st.session_state.generated_code,
            file_name=file_name,
            mime="text/plain"
        )

        # Additional information based on tool type
        if tool_type == "ansible":
            st.info("To use this Ansible playbook, save it as a .yml file and run it with `ansible-playbook filename.yml`")
        elif tool_type == "docker":
            st.info("To build this Docker image, save as 'Dockerfile' and run `docker build -t your-image-name .`")
        elif tool_type == "terraform":
            st.info("To use this Terraform code, save it as main.tf, run `terraform init` followed by `terraform apply`")

# Run the app
if __name__ == "__main__":
    main()